#!/usr/bin/env python3
"""
tests/test_vector_knowledge_base.py
------------------------------------
M5StickS3 灵宠伴侣长程向量知识库 (LingBuddyVectorStore) 单元测试
- 覆盖维度：
  1. SQLite 数据表自动初始化与持久化写入
  2. 文本特征提取器 (TextVectorizer) 与 N-Gram 编码正确性
  3. 余弦相似度 (Cosine Similarity) 计算与归一化
  4. BLE 0xFFB1 分块记忆流导入与重组索引
  5. Top-K 语义检索召回率与相似度排序检验
  6. RAG Prompt 上下文组装与长度约束
"""

import os
import sys
import tempfile
import pytest

from scripts.lingbuddy_vector_store import (
    TextVectorizer,
    cosine_similarity,
    LingBuddyVectorStore
)


def test_text_vectorizer_and_cosine_similarity():
    vectorizer = TextVectorizer(n_gram=2, max_features=128)
    corpus = [
        "明天我要去上海参加会议",
        "今天天气非常晴朗适合去公园散步",
        "帮我查询明天的天气预报"
    ]
    vectorizer.fit(corpus)

    v1 = vectorizer.transform("上海出差会议")
    v2 = vectorizer.transform("明天我要去上海")
    v3 = vectorizer.transform("今天天气晴朗去散步")

    # v1 与 v2 应该有明显相似度
    sim_12 = cosine_similarity(v1, v2)
    sim_13 = cosine_similarity(v1, v3)

    assert sim_12 > 0.1, f"包含重叠词'上海'与'会议'的向量相似度应大于0.1: {sim_12}"
    assert sim_12 > sim_13, f"语义相关的文本相似度 ({sim_12}) 应当高于无关文本 ({sim_13})"


def test_vector_store_crud_and_search():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        tmp_db = tmp.name

    try:
        store = LingBuddyVectorStore(db_path=tmp_db)
        stats = store.get_stats()
        assert stats["total_dialogue_chunks"] == 0
        assert stats["total_diaries"] == 0

        # 写入对话轮次
        id1 = store.add_dialogue_turn("user", "今天晚上我想吃意大利面")
        id2 = store.add_dialogue_turn("assistant", "好呀主人，番茄肉酱意面是个很棒的选择！")
        assert id1 > 0 and id2 > 0

        # 写入日记
        d_id = store.add_diary_entry("今天听主人提到了意大利面，悄悄口水都要流出来啦~", intimacy_level=2)
        assert d_id > 0

        stats = store.get_stats()
        assert stats["total_dialogue_chunks"] == 2
        assert stats["total_diaries"] == 1

        # 执行语义相似度检索
        results = store.search("意大利面", top_k=3)
        assert len(results) >= 2
        assert any("意大利面" in r["content"] for r in results)
        # 结果应按相似度评分降序排列
        for i in range(len(results) - 1):
            assert results[i]["score"] >= results[i + 1]["score"]

        # 测试 RAG Prompt 上下文生成
        rag_text = store.export_rag_context("今晚吃什么", max_chars=300)
        assert "意大利面" in rag_text
        assert "【来自 StickS3 伴侣长程记忆库的相关记忆检索】" in rag_text

    finally:
        if os.path.exists(tmp_db):
            os.remove(tmp_db)


def test_import_from_ble_stream():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        tmp_db = tmp.name

    try:
        store = LingBuddyVectorStore(db_path=tmp_db)
        ble_payload = [
            {"role": "user", "content": "我的猫叫咪咪"},
            {"role": "assistant", "content": "收到，主人有一只可爱的小猫咪叫咪咪。"}
        ]
        count = store.import_from_ble_stream(ble_payload)
        assert count == 2

        results = store.search("猫咪的名字")
        assert len(results) > 0
        assert "咪咪" in results[0]["content"]
    finally:
        if os.path.exists(tmp_db):
            os.remove(tmp_db)
