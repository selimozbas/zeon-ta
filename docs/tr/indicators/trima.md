# Üçgen Hareketli Ortalama (TRIMA)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/trima.md)

`zeonta.trima()` — An SMA of an SMA, weighting the middle of the window most heavily.

## Ne ölçer

Bir [sma](sma.md)'nın [sma](sma.md)'sı, iki pencere boyutu, birleşik etkinin her barı eşit ağırlıklandırmak yerine pencerenin ortasını en ağır şekilde ağırlıklandıracak şekilde seçilmiştir — `sma`'nın dikdörtgen şekli yerine üçgen bir ağırlıklandırma şekli.

## Formül

```text
Çift uzunluk: TRIMA = SMA(SMA(Kapanış, n/2), n/2+1); Tek uzunluk: TRIMA = SMA(SMA(Kapanış, (n+1)/2), (n+1)/2)
```

## Parametreler

**Gerekli girdiler:** `close`

| Parametre | Varsayılan |
| --- | --- |
| `length` | `20` |

## Döndürdükleri

| Kolon |
| --- |
| `TRIMA_20` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.trima(df['close']).tail(3)
```

```text
date
2024-10-25    90.931086
2024-10-26    90.872321
2024-10-27    90.777766
Name: TRIMA_20, dtype: float64
```

**Accessor biçimi:** `df.zta.trima(...)`

## Nasıl okunur

Herhangi bir hareketli ortalama gibi okunur. Aynı uzunluktaki bir `sma`'dan daha pürüzsüzdür (orta-ağırlıklandırma, pencerenin her iki ucundaki gürültüyü bastırır), bedeli ise daha uzun bir etkin gecikmedir.

## Dikkat edilmesi gerekenler

Özel bir uç durum yok — düz bir çift SMA geçişi.

## Kaynak

Formül kaynağı: [https://tulipindicators.org/trima](https://tulipindicators.org/trima)
