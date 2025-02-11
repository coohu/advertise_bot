import pandas as pd
import numpy as np
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
import evaluate
import torch
from typing import Dict, List

class CopywritingTrainer:
    def __init__(
        self,
        model_name: str = "mistralai/Mistral-7B-v0.1",
        max_length: int = 512
    ):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name)
        self.max_length = max_length
        
    def prepare_dataset(
        self,
        data: List[Dict[str, str]],
        train_ratio: float = 0.8
    ) -> tuple:
        """
        准备训练数据集
        data: 包含 'product_info' 和 'ad_copy' 字段的数据列表
        """
        # 构建提示模板
        def create_prompt(example):
            template = f"""产品信息：{example['product_info']}
            任务：请为上述产品创作一段富有创意的广告文案。
            创意广告文案：{example['ad_copy']}
            """
            return template

        # 数据预处理
        processed_data = []
        for item in data:
            prompt = create_prompt(item)
            processed_data.append({
                "text": prompt
            })

        # 转换为Dataset格式
        dataset = Dataset.from_pandas(pd.DataFrame(processed_data))
        
        # 分割训练集和验证集
        split_dataset = dataset.train_test_split(
            train_size=train_ratio,
            shuffle=True,
            seed=42
        )
        
        return split_dataset["train"], split_dataset["test"]

    def tokenize_function(self, examples):
        """将文本转换为token"""
        return self.tokenizer(
            examples["text"],
            padding="max_length",
            truncation=True,
            max_length=self.max_length,
            return_tensors="pt"
        )

    def train(
        self,
        train_dataset,
        eval_dataset,
        output_dir: str = "./copywriting_model",
        num_train_epochs: int = 3,
        per_device_train_batch_size: int = 4,
        gradient_accumulation_steps: int = 4,
        learning_rate: float = 2e-5,
    ):
        """训练模型"""
        # 设置训练参数
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=num_train_epochs,
            per_device_train_batch_size=per_device_train_batch_size,
            gradient_accumulation_steps=gradient_accumulation_steps,
            learning_rate=learning_rate,
            weight_decay=0.01,
            logging_dir="./logs",
            logging_steps=100,
            evaluation_strategy="steps",
            eval_steps=500,
            save_strategy="steps",
            save_steps=500,
            load_best_model_at_end=True,
        )

        # 准备数据整理器
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False
        )

        # 设置评估指标
        metric = evaluate.load("rouge")

        def compute_metrics(eval_pred):
            predictions, labels = eval_pred
            decoded_preds = self.tokenizer.batch_decode(
                predictions, skip_special_tokens=True
            )
            decoded_labels = self.tokenizer.batch_decode(
                labels, skip_special_tokens=True
            )
            result = metric.compute(
                predictions=decoded_preds,
                references=decoded_labels,
                use_stemmer=True
            )
            return {
                "rouge1": result["rouge1"],
                "rouge2": result["rouge2"],
                "rougeL": result["rougeL"]
            }

        # 初始化训练器
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            data_collator=data_collator,
            compute_metrics=compute_metrics,
            tokenizer=self.tokenizer,
        )

        # 开始训练
        trainer.train()
        
        # 保存模型
        trainer.save_model()
        self.tokenizer.save_pretrained(output_dir)

    def generate_ad_copy(
        self,
        product_info: str,
        max_new_tokens: int = 200,
        temperature: float = 0.8
    ) -> str:
        """生成广告文案"""
        prompt = f"""产品信息：{product_info}
        任务：请为上述产品创作一段富有创意的广告文案。
        创意广告文案："""
        
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            max_length=self.max_length,
            truncation=True
        )

        # 生成文案
        outputs = self.model.generate(
            inputs["input_ids"],
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_p=0.9,
            do_sample=True,
        )
        
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

# 使用示例
def main():
    # 示例数据
    sample_data = [
        {
            "product_info": "智能手表，具有心率监测、运动追踪功能，支持防水",
            "ad_copy": "聆听心跳的韵律，追踪生命的活力。让时间不仅仅是流逝，更是生命的计量。防水科技，让你自由畅游。这不只是一款手表，更是你的健康守护者。"
        },
        # ... 更多训练数据
    ]
    
    # 初始化训练器
    trainer = CopywritingTrainer()
    
    # 准备数据集
    train_dataset, eval_dataset = trainer.prepare_dataset(sample_data)
    
    # 训练模型
    trainer.train(train_dataset, eval_dataset)
    
    # 生成示例
    new_product = "便携式咖啡机，可以随时随地冲泡新鲜咖啡，一键操作"
    generated_copy = trainer.generate_ad_copy(new_product)
    print(f"生成的广告文案：\n{generated_copy}")

if __name__ == "__main__":
    main()