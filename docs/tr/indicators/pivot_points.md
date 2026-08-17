# Pivot Noktaları

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/pivot_points.md)

`zeonta.pivot_points()` — Classic or Fibonacci pivot levels derived from the previous bar.

## Ne ölçer

Bugün için, daha piyasa açılmadan dünün aralığından hesaplanan bir seviye ızgarası. Borsa salonundaki yatırımcılar bunları tam da grafik gerektirmedikleri ve seans içinde yeniden hesaplanmaları gerekmediği için kullanırdı.

## Formül

```text
Klasik: Pivot = (Yüksek + Düşük + Kapanış) / 3; R1 = 2xPivot - Düşük; S1 = 2xPivot - Yüksek; R2 = Pivot + (Yüksek - Düşük); S2 = Pivot - (Yüksek - Düşük); R3 = Yüksek + 2x(Pivot - Düşük); S3 = Düşük - 2x(Yüksek - Pivot). Fibonacci: R1/S1 = Pivot +/- 0,382x(Yüksek - Düşük); R2/S2 = Pivot +/- 0,618x(Yüksek - Düşük); R3/S3 = Pivot +/- 1,0x(Yüksek - Düşük)
```

## Parametreler

**Gerekli girdiler:** `high`, `low`, `close`

| Parametre | Varsayılan |
| --- | --- |
| `kind` | `'classic'` |

## Döndürdükleri

| Kolon |
| --- |
| `PP_classic` |
| `R1_classic` |
| `R2_classic` |
| `R3_classic` |
| `S1_classic` |
| `S2_classic` |
| `S3_classic` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.pivot_points(df['high'], df['low'], df['close'], kind='classic').tail(2)
```

```text
            PP_classic  R1_classic  R2_classic  R3_classic  S1_classic  S2_classic  S3_classic
date                                                                                          
2024-10-26   90.229367   90.693933   91.291667   91.756233   89.631633   89.167067   88.569333
2024-10-27   89.485600   89.875200   90.631400   91.021000   88.729400   88.339800   87.583600
```

**Accessor biçimi:** `df.zta.pivot_points(...)`

## Nasıl okunur

Merkezî pivot günün referansıdır: üzerinde işlem görmek boğa seansı, altında ayı seansıdır. R1/S1 sıradan bir günde ulaşılan seviyelerdir; R3/S3 ancak büyük bir günde devreye girer. Günlük pivotlar için günlük bar, haftalık pivotlar için haftalık bar verin.

## Dikkat edilmesi gerekenler

Pivotlar analiz değil aritmetiktir — önceki barın aralığının ötesinde bir bilgi taşımazlar ve esas olarak ortak bir referans ızgarası olarak işe yararlar. Gerçek bir seans sınırı olmayan enstrümanlarda çok daha az anlamlıdırlar.
