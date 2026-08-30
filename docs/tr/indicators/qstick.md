# Qstick

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/qstick.md)

`zeonta.qstick()` — SMA of each bar's own Close-minus-Open body, a simple candle-bias gauge.

## Ne ölçer

Tushar Chande'nin en basit indikatörü: her barın kendi gövdesinin (Kapanış eksi Açılış) hareketli ortalaması. [bop](bop.md)'tan farklıdır — o, aynı kapanış-eksi-açılış farkını doğrudan yumuşatmak yerine barın kendi yüksek-düşük aralığına göre normalize eder.

## Formül

```text
QS = SMA(Kapanış - Açılış, length)
```

## Parametreler

**Gerekli girdiler:** `open`, `close`

| Parametre | Varsayılan |
| --- | --- |
| `length` | `10` |

## Döndürdükleri

| Kolon |
| --- |
| `QS_10` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.qstick(df['open'], df['close']).tail(3)
```

```text
date
2024-10-25   -0.24931
2024-10-26   -0.32247
2024-10-27   -0.32389
Name: QS_10, dtype: float64
```

**Accessor biçimi:** `df.zta.qstick(...)`

## Nasıl okunur

Pozitif olması, pencere boyunca kapanışların açılışların üzerinde istikrarlı şekilde oturduğu (yükseliş yönlü gövde eğilimi) anlamına gelir; negatif olması tam tersidir. Qstick'in kendi sıfır çizgisini kesmesi standart okumadır.

## Dikkat edilmesi gerekenler

Özel bir uç durum yok — basit bir bar-gövdesi farkının düz bir SMA'sı.

## Kaynak

Formül kaynağı: [https://corporatefinanceinstitute.com/resources/knowledge/trading-investing/qstick-indicator/](https://corporatefinanceinstitute.com/resources/knowledge/trading-investing/qstick-indicator/)
