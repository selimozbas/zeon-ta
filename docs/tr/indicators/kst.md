# Pring'in Know Sure Thing'i (KST)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/kst.md)

`zeonta.kst()` — Four weighted-and-smoothed ROC cycles combined into one long-cycle momentum line.

## Ne ölçer

Martin Pring, ayrı ayrı yumuşatılmış dört [roc](roc.md) döngüsünü tek bir çizgide birleştirir, daha uzun döngüleri daha ağır ağırlıklandırır — bunların önemli momentum kaymalarını kısa vadeli gürültüden daha iyi yakaladığı fikrine dayanarak.

## Formül

```text
KST = 1*SMA(ROC(roc1),sma1) + 2*SMA(ROC(roc2),sma2) + 3*SMA(ROC(roc3),sma3) + 4*SMA(ROC(roc4),sma4)
```

## Parametreler

**Gerekli girdiler:** `close`

| Parametre | Varsayılan |
| --- | --- |
| `roc1` | `10` |
| `roc2` | `15` |
| `roc3` | `20` |
| `roc4` | `30` |
| `sma1` | `10` |
| `sma2` | `10` |
| `sma3` | `10` |
| `sma4` | `15` |
| `signal` | `9` |

## Döndürdükleri

| Kolon |
| --- |
| `KST_10_15_20_30` |
| `KSTs_10_15_20_30` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.kst(df['close']).tail(3)
```

```text
            KST_10_15_20_30  KSTs_10_15_20_30
date                                         
2024-10-25       -10.961943        -10.673602
2024-10-26       -12.683430        -10.766873
2024-10-27       -14.701257        -11.235720
```

**Accessor biçimi:** `df.zta.kst(...)`

## Nasıl okunur

[macd](macd.md) gibi okunur: KST ile kendi sinyal çizgisi arasındaki kesişim, ya da KST'nin kendi sıfır çizgisini kesmesi, iki standart okumadır.

## Dikkat edilmesi gerekenler

Toplamda dokuz parametre (dört ROC uzunluğu, dört eşleşen SMA uzunluğu, bir sinyal uzunluğu) — Pring'in kendi günlük-grafik varsayılanları, sembol başına ayarlanmak yerine genellikle olduğu gibi kullanılır.

## Kaynak

Formül kaynağı: [https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/prings-know-sure-thing-kst](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/prings-know-sure-thing-kst)
