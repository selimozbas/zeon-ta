# Hacim Ağırlıklı Hareketli Ortalama (VWMA)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/vwma.md)

`zeonta.vwma()` — Simple moving average, but each bar weighted by its own volume.

## Ne ölçer

[sma](sma.md), o barda ne kadar işlem gördüğüne bakmaksızın penceredeki her barı eşit muamele eder; VWMA ise ağır-hacimli bir barın ortalamayı kendi kapanışına doğru, sakin bir bardan daha fazla çekmesine izin verir — [vwap](vwap.md)'ın kullandığı aynı hacim-ağırlıklandırma fikri, ama her seansta sıfırlanmak yerine sabit bir yuvarlanan pencere üzerinden.

## Formül

```text
VWMA = Toplam(Kapanış * Hacim, n) / Toplam(Hacim, n)
```

## Parametreler

**Gerekli girdiler:** `close`, `volume`

| Parametre | Varsayılan |
| --- | --- |
| `length` | `20` |

## Döndürdükleri

| Kolon |
| --- |
| `VWMA_20` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.vwma(df['close'], df['volume']).tail(3)
```

```text
date
2024-10-25    90.613110
2024-10-26    90.553374
2024-10-27    90.473801
Name: VWMA_20, dtype: float64
```

**Accessor biçimi:** `df.zta.vwma(...)`

## Nasıl okunur

Herhangi bir hareketli ortalama gibi okunur — fiyatın üstünden/altından geçmesi ya da kendi eğimi — farkı, alışılmadık derecede ağır hacimdeki bir kırılmanın burada aynı uzunluktaki düz bir SMA'dan daha belirgin görünmesidir.

## Dikkat edilmesi gerekenler

Pencerenin toplam hacmi tam olarak `0` olduğunda (o pencerede hiç işlem olmamış) tanımsız bir bölüm yerine `NaN` olur.

## Kaynak

Formül kaynağı: [https://www.tradingview.com/support/solutions/43000592293-volume-weighted-moving-average-vwma/](https://www.tradingview.com/support/solutions/43000592293-volume-weighted-moving-average-vwma/)
