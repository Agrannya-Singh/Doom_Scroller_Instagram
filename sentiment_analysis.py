"""
Sentiment analysis for Instagram reels using multilingual models
"""

import torch
import numpy as np
import pandas as pd
from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification,
    AlbertForSequenceClassification, RobertaForSequenceClassification,
    Trainer, TrainingArguments
)
from datasets import Dataset, Value
from sklearn.metrics import accuracy_score, f1_score
from collections import Counter
import re

from config import CONFIG, DEVICE, NEUTRAL_KEYWORDS
from utils import preprocess_text, detect_language

class ReelSentimentAnalyzer:
    def __init__(self):
        self.device = DEVICE
        self._initialize_models()

    def _initialize_models(self):
        """Initialize and configure all models"""
        print("\nInitializing Sentiment Analysis Models...")

        # English emotion model
        print("Loading English Emotion Model...")
        self.emotion_tokenizer = AutoTokenizer.from_pretrained("finiteautomata/bertweet-base-emotion-analysis")
        self.emotion_model = AutoModelForSequenceClassification.from_pretrained(
            "finiteautomata/bertweet-base-emotion-analysis"
        ).to(self.device)

        # English sentiment model
        print("Loading English Sentiment Model...")
        self.sentiment_tokenizer = AutoTokenizer.from_pretrained("cardiffnlp/twitter-roberta-base-sentiment-latest")
        self.sentiment_model = RobertaForSequenceClassification.from_pretrained(
            "cardiffnlp/twitter-roberta-base-sentiment-latest",
            ignore_mismatched_sizes=True
        ).to(self.device)

        # Hindi/English model
        print("Loading Indic-BERT Model for Hindi/Hinglish...")
        self.hindi_tokenizer = AutoTokenizer.from_pretrained("ai4bharat/indic-bert")
        self.hindi_model = AlbertForSequenceClassification.from_pretrained(
            "ai4bharat/indic-bert",
            num_labels=3,
            id2label={0: "negative", 1: "neutral", 2: "positive"},
            label2id={"negative": 0, "neutral": 1, "positive": 2}
        ).to(self.device)

        self.hindi_label2id = self.hindi_model.config.label2id
        print("Models Initialized.")

        # Emotion to sentiment mapping
        self.emotion_map = {
            "joy": "positive", "love": "positive", "happy": "positive",
            "anger": "negative", "sadness": "negative", "fear": "negative",
            "surprise": "neutral", "neutral": "neutral", "disgust": "negative", "shame": "negative"
        }

    def train_hindi_model(self, train_data, eval_data=None):
        """Fine-tune the Hindi/English model on labeled data"""
        print("\nStarting Hindi model training...")

        # Convert to dataset
        train_dataset = Dataset.from_pandas(pd.DataFrame(train_data))

        def map_labels_to_ids(examples):
            labels = []
            for label_str in examples["label"]:
                if label_str in self.hindi_label2id:
                    labels.append(self.hindi_label2id[label_str])
                else:
                    print(f"Warning: Unexpected label '{label_str}'. Mapping to neutral.")
                    labels.append(self.hindi_label2id["neutral"])
            examples["label"] = labels
            return examples

        train_dataset = train_dataset.map(map_labels_to_ids, batched=True)
        train_dataset = train_dataset.cast_column("label", Value("int64"))

        def tokenize_function(examples):
            return self.hindi_tokenizer(
                examples["text"],
                padding="max_length",
                truncation=True,
                max_length=CONFIG["max_length"]
            )

        tokenized_train = train_dataset.map(tokenize_function, batched=True)

        # Training arguments
        training_args = TrainingArguments(
            output_dir="./results",
            eval_strategy="epoch" if eval_data else "no",
            per_device_train_batch_size=CONFIG["batch_size"],
            per_device_eval_batch_size=CONFIG["batch_size"],
            learning_rate=CONFIG["learning_rate"],
            num_train_epochs=CONFIG["num_train_epochs"],
            weight_decay=0.01,
            save_strategy="no",
            logging_dir='./logs',
            logging_steps=10,
            report_to="none"
        )

        def compute_metrics(p):
            predictions, labels = p
            predictions = np.argmax(predictions, axis=1)
            return {
                "accuracy": accuracy_score(labels, predictions),
                "f1": f1_score(labels, predictions, average="weighted")
            }

        # Trainer
        eval_dataset_processed = None
        if eval_data:
            eval_dataset = Dataset.from_pandas(pd.DataFrame(eval_data))
            eval_dataset = eval_dataset.map(map_labels_to_ids, batched=True)
            eval_dataset_processed = eval_dataset.cast_column("label", Value("int64")).map(tokenize_function, batched=True)

        trainer = Trainer(
            model=self.hindi_model,
            args=training_args,
            train_dataset=tokenized_train,
            eval_dataset=eval_dataset_processed,
            compute_metrics=compute_metrics if eval_data else None,
        )

        # Train
        trainer.train()

        # Save the fine-tuned model
        print("Saving fine-tuned Hindi model...")
        self.hindi_model.save_pretrained("./fine_tuned_hindi_sentiment")
        self.hindi_tokenizer.save_pretrained("./fine_tuned_hindi_sentiment")
        print("Hindi model training complete.")

    def analyze_content(self, text):
        """Main analysis function with improved confidence handling"""
        processed = preprocess_text(text)

        if not processed:
            return "neutral", 0.5, {"reason": "empty_text"}

        lang = detect_language(processed)

        # Check for neutral keywords first
        if any(re.search(rf"\b{re.escape(kw)}\b", processed.lower()) for kw in NEUTRAL_KEYWORDS):
            return "neutral", 0.9, {"reason": "neutral_keyword"}

        try:
            if lang in ("hi", "hi-latin"):
                return self._analyze_hindi_content(processed)
            else:
                return self._analyze_english_content(processed)
        except Exception as e:
            print(f"Analysis error for text '{processed[:50]}...': {e}")
            return "neutral", 0.5, {"error": str(e), "original_text": text[:50]}

    def _analyze_hindi_content(self, text):
        """Analyze Hindi content with fine-tuned model"""
        inputs = self.hindi_tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=CONFIG["max_length"]
        ).to(self.device)

        with torch.no_grad():
            outputs = self.hindi_model(**inputs)
            probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
            pred_idx = torch.argmax(probs).item()
            confidence = probs[0][pred_idx].item()
            label = self.hindi_model.config.id2label[pred_idx]

        return label, confidence, {"model": "fine-tuned-indic-bert", "lang": "hi"}

    def _analyze_english_content(self, text):
        """Analyze English content with ensemble approach"""
        # Emotion analysis
        emotion_inputs = self.emotion_tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=CONFIG["max_length"]
        ).to(self.device)

        with torch.no_grad():
            emotion_outputs = self.emotion_model(**emotion_inputs)
            emotion_probs = torch.nn.functional.softmax(emotion_outputs.logits, dim=-1)
            emotion_pred = torch.argmax(emotion_probs).item()
            emotion_label = self.emotion_model.config.id2label[emotion_pred]
            emotion_score = emotion_probs[0][emotion_pred].item()

        # Sentiment analysis
        sentiment_inputs = self.sentiment_tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=CONFIG["max_length"]
        ).to(self.device)

        with torch.no_grad():
            sentiment_outputs = self.sentiment_model(**sentiment_inputs)
            sentiment_probs = torch.nn.functional.softmax(sentiment_outputs.logits, dim=-1)
            sentiment_pred = torch.argmax(sentiment_probs).item()

        sentiment_label_mapping = {0: 'negative', 1: 'neutral', 2: 'positive'}
        sentiment_label = sentiment_label_mapping.get(sentiment_pred, 'neutral')
        sentiment_score = sentiment_probs[0][sentiment_pred].item()

        # Combine results
        mapped_emotion = self.emotion_map.get(emotion_label, "neutral")

        # Prioritize high-confidence sentiment
        if sentiment_score > CONFIG["confidence_threshold"]:
            final_label = sentiment_label
            final_confidence = sentiment_score
            reason = "high_sentiment_confidence"
        elif emotion_score > CONFIG["confidence_threshold"] and mapped_emotion != "neutral":
            final_label = mapped_emotion
            final_confidence = emotion_score
            reason = "high_emotion_confidence"
        else:
            # Fallback mechanism
            if sentiment_label == mapped_emotion and sentiment_label != "neutral":
                final_label = sentiment_label
                final_confidence = (sentiment_score + emotion_score) / 2
                reason = "emotion_sentiment_agreement"
            elif sentiment_label != "neutral" and sentiment_score > emotion_score and sentiment_score > 0.4:
                final_label = sentiment_label
                final_confidence = sentiment_score * 0.9
                reason = "sentiment_slightly_higher"
            elif mapped_emotion != "neutral" and emotion_score > sentiment_score and emotion_score > 0.4:
                final_label = mapped_emotion
                final_confidence = emotion_score * 0.9
                reason = "emotion_slightly_higher"
            else:
                final_label = "neutral"
                final_confidence = 0.6
                reason = "fallback_to_neutral"

        return final_label, final_confidence, {
            "emotion_label": emotion_label,
            "emotion_score": emotion_score,
            "sentiment_label": sentiment_label,
            "sentiment_score": sentiment_score,
            "mapped_emotion": mapped_emotion,
            "model": "ensemble",
            "lang": "en",
            "reason": reason
        }

    def analyze_reels(self, reels, max_to_analyze=100):
        """Batch analysis with improved neutral handling"""
        print(f"\n--- Starting Sentiment Analysis ({max_to_analyze} reels) ---")

        results = Counter()
        detailed_results = []

        for i, reel in enumerate(reels[:max_to_analyze], 1):
            caption = getattr(reel, 'caption_text', '') or getattr(reel, 'caption', '') or ''
            print(f"Analyzing sentiment for reel {i}/{max_to_analyze} (ID: {reel.id})...")

            label, confidence, details = self.analyze_content(caption)
            results[label] += 1

            detailed_results.append({
                "reel_id": reel.id,
                "text": caption,
                "label": label,
                "confidence": confidence,
                "details": details
            })

        print("\nInitial Sentiment Distribution:", dict(results))

        # Post-analysis neutral reduction
        total_analyzed = sum(results.values())
        if total_analyzed > 0 and results["neutral"] / total_analyzed > CONFIG["neutral_reanalysis_threshold"]:
            print(f"High neutral count ({results['neutral']}). Attempting to re-analyze...")
            self._reduce_neutrals(results, detailed_results)
            print("Sentiment distribution after re-analysis:", dict(results))

        print("Sentiment Analysis Complete.")
        return results, detailed_results

    def _reduce_neutrals(self, results, detailed_results):
        """Apply additional techniques to reduce neutral classifications"""
        neutrals_to_recheck = [item for item in detailed_results if item["label"] == "neutral" and item["confidence"] < 0.8]
        print(f"Re-checking {len(neutrals_to_recheck)} neutral reels...")

        for item in neutrals_to_recheck:
            original_text = item["text"]
            processed_text = preprocess_text(original_text)
            text_lower = processed_text.lower()

            # Strong positive/negative keyword analysis
            pos_keywords_strong = {"amazing", "love", "best", "fantastic", "awesome", "superb", "great",
                                  "अद्भुत", "शानदार", "बहुत अच्छा", "मज़ेदार"}
            neg_keywords_strong = {"hate", "worst", "bad", "terrible", "awful", "disappointed", "horrible", "cringe",
                                  "खराब", "बेकार", "बहुत बुरा", "घटिया"}

            is_strong_pos = any(re.search(rf"\b{re.escape(kw)}\b", text_lower) for kw in pos_keywords_strong)
            is_strong_neg = any(re.search(rf"\b{re.escape(kw)}\b", text_lower) for kw in neg_keywords_strong)

            if is_strong_pos and not is_strong_neg:
                results["neutral"] -= 1
                results["positive"] += 1
                item.update({
                    "label": "positive",
                    "confidence": min(0.95, item["confidence"] + 0.3),
                    "reanalyzed": True,
                    "reanalysis_reason": "strong_pos_keywords"
                })
            elif is_strong_neg and not is_strong_pos:
                results["neutral"] -= 1
                results["negative"] += 1
                item.update({
                    "label": "negative",
                    "confidence": min(0.95, item["confidence"] + 0.3),
                    "reanalyzed": True,
                    "reanalysis_reason": "strong_neg_keywords"
                })
