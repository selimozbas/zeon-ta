# Düzeltilmiş Hareketli Ortalama (SMMA)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/smma.md)

`zeonta.smma()` — Wilder's exponential smoothing, exposed as its own moving average.

## Ne ölçer

J. Welles Wilder'ın *New Concepts in Technical Trading Systems* (1978) kitabında `rsi`, `atr` ve `adx` boyunca kullandığı tam recursion, burada bu üçünün içinde gömülü kalmak yerine kendi başına bir çizgi olarak sunuluyor. `ema`'ya cebirsel olarak özdeştir, sadece `alpha = 2/(n+1)` yerine `alpha = 1/n` kullanır — aynı formül şekli, yalnızca daha yumuşak bir düzeltme sabiti; Wilder'ın araçlarının aynı uzunluktaki düz bir EMA eşdeğerinden bir tık daha sakin hissettirmesinin nedeni budur.

## Formül

```text
SMMA[t] = SMMA[t-1] + (Kapanış[t] - SMMA[t-1]) / n, ilk n barın düz SMA'sıyla tohumlanır
```

## Parametreler

**Gerekli girdiler:** `close`

| Parametre | Varsayılan |
| --- | --- |
| `length` | `9` |

## Döndürdükleri

| Kolon |
| --- |
| `SMMA_9` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.smma(df['close'], length=9).tail(3)
```

```text
date
2024-10-25    90.639953
2024-10-26    90.470959
2024-10-27    90.249985
Name: SMMA_9, dtype: float64
```

**Accessor biçimi:** `df.zta.smma(...)`

## Nasıl okunur

Diğer hareketli ortalamalar gibi okuyun — trend yönü, dinamik destek/direnç — ama aynı belirtilen uzunluktaki bir EMA'dan belirgin biçimde daha fazla gecikmesini bekleyin, çünkü `alpha=1/n` her zaman EMA'nın `2/(n+1)` değerinden küçüktür (n>1 için). Ayrıca `wma`'nın pencere kenarındaki sert kesintisinin aksine eski fiyatları hiçbir zaman tam olarak unutmaz; ısınmadan sonraki her bar küçülen bir ağırlık payı taşımaya devam eder.

## Dikkat edilmesi gerekenler

Ne StockCharts ne de Wikipedia SMMA'yı kendi başına adlandırılmış bir indikatör olarak belgeler — bu sitelerde yalnızca RSI/ATR/ADX'in içine gömülü olarak görünür. Buradaki varsayılan uzunluk (9), Wilder'ın RSI/ATR/ADX için kullandığı 14 kuralı yerine TradingView'in kendi özel Smoothed Moving Average sayfasını izler, çünkü tek başına bir indikatör olarak SMMA için kanonik bir varsayılan belirten tek bir kaynak yoktur; recursion'un kendisi MetaTrader'ın MQL5 dokümantasyonuna karşı bağımsız olarak doğrulanmıştır.

## Kaynak

Formül kaynağı: [https://www.tradingview.com/support/solutions/43000591343-smoothed-moving-average/](https://www.tradingview.com/support/solutions/43000591343-smoothed-moving-average/)
