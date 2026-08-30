# Basıklık

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/kurtosis.md)

`zeonta.kurtosis()` — Adjusted Fisher-Pearson excess kurtosis: how fat-tailed the recent distribution is.

## Ne ölçer

[skewness](skewness.md)'in kardeş şekil ölçüsü: hangi tarafın kuyruğunun daha uzun olduğu değil, normal bir dağılıma kıyasla *her iki* kuyruğun ne kadar şişman olduğu — pencerenin yayılımının ne kadarının eşit dağılmak yerine birkaç uç bardan geldiği.

## Formül

```text
Düzeltilmiş Fisher-Pearson fazlalık katsayısı: G2 = ((n-1)/((n-2)(n-3))) * ((n+1)g2 + 6), g2 = m4/m2^2 - 3, pandas'ın kendi yuvarlanan .kurt()'unun kullandığı aynı yanlılık-düzeltmeli formül
```

## Parametreler

**Gerekli girdiler:** `close`

| Parametre | Varsayılan |
| --- | --- |
| `length` | `20` |

## Döndürdükleri

| Kolon |
| --- |
| `KURT_20` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.kurtosis(df['close']).tail(3)
```

```text
date
2024-10-25   -0.164868
2024-10-26   -0.344097
2024-10-27   -0.100764
Name: KURT_20, dtype: float64
```

**Accessor biçimi:** `df.zta.kurtosis(...)`

## Nasıl okunur

`0`, normal bir dağılımın kuyrukları gibi okunur. Pozitif (şişman kuyruklar), pencerenin yayılımına birkaç uç barın hakim olduğu anlamına gelir — çoğunlukla sakin olup ara sıra keskin şoklar üreten bir piyasanın deseni. Negatif (ince kuyruklar), hareketlerin büyüklük olarak alışılmadık derecede tek tip olduğu anlamına gelir.

## Dikkat edilmesi gerekenler

Kararlı olması için `skewness`'ten daha fazla noktaya ihtiyaç duyar (dördüncü moment tahmini kısa bir pencerede daha da gürültülüdür) ve onun gibi tamamen düz bir pencerede `NaN` olur.

## Kaynak

Formül kaynağı: [https://en.wikipedia.org/wiki/Kurtosis](https://en.wikipedia.org/wiki/Kurtosis)
