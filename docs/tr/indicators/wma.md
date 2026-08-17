# Ağırlıklı Hareketli Ortalama (WMA)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/wma.md)

`zeonta.wma()` — Moving average giving linearly increasing weight to more recent closes.

## Ne ölçer

Pencereyi ele alış biçimiyle `sma` ve `ema` arasında tam ortada durur: her bar yine sabit, öngörülebilir bir ağırlık alır (EMA'nın teknik olarak hiç sıfıra ulaşmayan azalmasının aksine), ama bu ağırlık artık SMA'nın tüm pencereyi eşit saymasının aksine, düz bir çizgi halinde son barları kayırır.

## Formül

```text
WMA = (P1 x n + P2 x (n-1) + ... + Pn x 1) / (n + (n-1) + ... + 1), burada P1 en son kapanış, Pn ise pencerede en eski kapanıştır
```

## Parametreler

**Gerekli girdiler:** `close`

| Parametre | Varsayılan |
| --- | --- |
| `length` | `20` |

## Döndürdükleri

| Kolon |
| --- |
| `WMA_20` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.wma(df['close'], length=20).tail(3)
```

```text
date
2024-10-25    90.600817
2024-10-26    90.449951
2024-10-27    90.245885
Name: WMA_20, dtype: float64
```

**Accessor biçimi:** `df.zta.wma(...)`

## Nasıl okunur

Tam olarak `sma` gibi okuyun — trend yönü, destek, kesişimler — ama son barlar daha fazla ağırlık taşıdığı için bir dönüşten sonra daha erken yön değiştirmesini bekleyin. Ayrıca başka birçok hareketli ortalamanın (Hull Hareketli Ortalaması gibi) gecikmeyi daha da azaltmak için zincirlediği temel yapı taşıdır.

## Dikkat edilmesi gerekenler

Doğrusal azalma, EMA'nın üssel azalmasına kıyasla çok daha yumuşak bir gecikme azaltmasıdır — aynı uzunlukta WMA, gecikme açısından EMA'dan çok SMA'ya daha yakındır. Ayrıca sabit uzunluklu her hareketli ortalamanın temel sınırlamasını devralır: uyarlanabilir :func:`~zeonta.kama`'nın aksine, hiçbir uzunluk hem trend yapan hem de dalgalanan bir piyasa için doğru değildir.

## Kaynak

Formül kaynağı: [https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/wma](https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/wma)
