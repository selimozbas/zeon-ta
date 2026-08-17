# Ortalama Gerçek Aralık (ATR)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/atr.md)

`zeonta.atr()` — Wilder-smoothed average of True Range — how much a symbol typically moves.

## Ne ölçer

Bu sembol bir barda tipik olarak ne kadar hareket eder? ATR bunu enstrümanın kendi biriminde yanıtlar. Gerçek aralık, önceki kapanışa göre oluşan boşluğu da içerdiği için, gece boşluk veren bir piyasada oynaklığı olduğundan küçük göstermez.

## Formül

```text
TR = max(En Yüksek - En Düşük, |En Yüksek - ÖncekiKapanış|, |En Düşük - ÖncekiKapanış|); ATR = TR'nin 14 periyot üzerinden Wilder-yumuşatılmış ortalaması (ilk ATR = HO(TR,14), sonra ATR = (ÖncekiATR x 13 + TR) / 14)
```

## Parametreler

**Gerekli girdiler:** `high`, `low`, `close`

| Parametre | Varsayılan |
| --- | --- |
| `length` | `14` |

## Döndürdükleri

| Kolon |
| --- |
| `ATR_14` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.atr(df['high'], df['low'], df['close'], length=14).tail(3)
```

```text
date
2024-10-25    1.198313
2024-10-26    1.194562
2024-10-27    1.221172
Name: ATR_14, dtype: float64
```

**Accessor biçimi:** `df.zta.atr(...)`

## Nasıl okunur

ATR, pozisyon büyüklüğü belirlemenin ve stop yerleştirmenin standart yoludur: 2 x ATR mesafesindeki bir stop, sakin bir tahvil ETF'inde de oynak bir küçük ölçekli hissede de aynı miktarda "alan" bırakır. ATR'nin yükselmesi koşulların genişlediği anlamına gelir, fiyatın yükseldiği anlamına değil.

## Dikkat edilmesi gerekenler

ATR yönsüzdür — bir çöküş ile bir sert yükseliş aynı değeri üretir. Ayrıca mutlak bir rakamdır; fiyatı bilmeden 5'lik bir ATR anlamsızdır. Semboller arasında karşılaştırmak istiyorsanız kapanışa bölün.
