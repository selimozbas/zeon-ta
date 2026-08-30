# Logaritmik Getiri

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/log_return.md)

`zeonta.log_return()` — Logarithmic return over a fixed bar lag.

## Ne ölçer

[roc](roc.md)'un istatistiksel kuzeni: aynı bar-gecikmeli karşılaştırma, yüzde yerine logaritmik oran olarak ifade edilir. Logaritmik getiriler zaman içinde toplanabilirdir (bir pencere boyunca tek-barlık log getirilerin toplamı, tüm pencerenin log getirisine eşittir), basit yüzde değişim ise değildir — bu kütüphanenin bir getiri serisi üzerindeki istatistiksel çalışmalarının (kendi `hurst_exponent`, `dfa` ve `sample_entropy`'si dahil) `roc` yerine bu biçimi kullanmasının nedeni budur.

## Formül

```text
LOGRET = ln(Kapanış[t] / Kapanış[t-n])
```

## Parametreler

**Gerekli girdiler:** `close`

| Parametre | Varsayılan |
| --- | --- |
| `length` | `1` |

## Döndürdükleri

| Kolon |
| --- |
| `LOGRET_1` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.log_return(df['close']).tail(3)
```

```text
date
2024-10-25   -0.004526
2024-10-26   -0.010905
2024-10-27   -0.007171
Name: LOGRET_1, dtype: float64
```

**Accessor biçimi:** `df.zta.log_return(...)`

## Nasıl okunur

Sıradan büyüklükteki hareketler için, logaritmik getiri ile basit yüzde getiri neredeyse aynıdır (`ln(1.01) ~= 0,00995`); büyük tek-barlık bir harekette daha belirgin şekilde ayrışırlar.

## Dikkat edilmesi gerekenler

Kesinlikle pozitif fiyatlar gerektirir — sıfır ya da negatif bir değerin `ln`'i tanımsızdır, bu burada bir istisna yerine `NaN` olarak ortaya çıkar.

## Kaynak

Formül kaynağı: [https://en.wikipedia.org/wiki/Rate_of_return](https://en.wikipedia.org/wiki/Rate_of_return)
