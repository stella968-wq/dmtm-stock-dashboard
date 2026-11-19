# 美股雙動能 (DMTM) 量化投資儀表板

> Dual-Momentum Trend Model (DMTM) US Stock Quantitative Dashboard

基於美股量化策略講義所打造之全功能互動式量化投資儀表板，整合 Barchart 雙榜交集篩選、Beneish M-Score / Altman Z-Score / Piotroski F-Score 即時財報排雷、分流估值、移動止盈與 70/30 核心衛星動態 Beta 資金配置。

## 🚀 核心四大模組
1. **模組一：Barchart 雙榜交集篩選器**
   - Barchart 官方 Top Stocks to Own 與 Top 100 Stocks to Buy 雙榜交集
   - 支援 CSV / Excel 上傳與表格文字直接貼上，毫秒級自動精準解析交集股票
2. **模組二：即時財報排雷（M/Z/F-Score）與 12 項指標打分**
   - 透過 yfinance 即時動態抓取財報計算 Beneish M-Score（排雷操縱）、Altman Z-Score（破產風險）與 Piotroski F-Score（基本面強度）
   - 12 項關鍵指標綜合打分（≥ 10 分合格），自動劃分「推薦建倉」、「可建倉」與「輕倉」三級建議
3. **模組三：個股分流估值、互動式 K 線圖與 15% 移動止盈**
   - 互動式 K 線圖、均線、成交量與 15% 移動止盈觸發線
   - 科技股 (Forward PE vs Trailing PE)、高成長股 (P/S < 5)、週期股 (P/B 0.8~1.5) 分流估值
   - 整合 Stock Analysis 與 CNN Markets 雙權威專家預測模型與共識評等
4. **模組四：70/30 核心衛星配置與動態 Beta 資金計算機**
   - 核心科技/AI 供應鏈佔 70%，衛星週期防禦佔 30%
   - 即時抓取 Beta 值，動態求解股票、VOO (大盤 ETF) 與現金的最佳比例（目標組合 β = 1.0 ~ 1.2）

## 📦 安裝與本地運行
```bash
pip install -r requirements.txt
streamlit run app.py
```
