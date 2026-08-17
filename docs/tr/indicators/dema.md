# Çift Üssel Hareketli Ortalama (DEMA)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/dema.md)

`zeonta.dema()` — EMA with roughly half the lag, by offsetting a single EMA with its own EMA.

## Ne ölçer

Tek bir EMA her zaman geride kalır, çünkü tanımı gereği hâlâ fiyata yetişmeye çalışıyordur. DEMA bu gecikmeyi EMA'yı ikinci kez yumuşatarak tahmin eder — EMA1 ile EMA2 arasındaki fark, EMA1'in ne kadar geride kaldığını kabaca gösterir — sonra bu farkı bir kez daha ekleyerek gecikmenin çoğunu iptal eder.

## Formül

```text
DEMA = (2 x EMA1) - EMA2, burada EMA1 = EMA(Kapanış, n) ve EMA2 = EMA(EMA1, n)
```

## Parametreler

**Gerekli girdiler:** `close`

| Parametre | Varsayılan |
| --- | --- |
| `length` | `20` |

## Döndürdükleri

| Kolon |
| --- |
| `DEMA_20` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.dema(df['close'], length=20).tail(3)
```

```text
date
2024-10-25    90.218397
2024-10-26    89.975636
2024-10-27    89.653624
Name: DEMA_20, dtype: float64
```

**Accessor biçimi:** `df.zta.dema(...)`

## Nasıl okunur

Tam olarak `ema` gibi okuyun — trend yönü, destek, kesişimler — ama dönüşleri daha erken bekleyin: düz bir doğrusal harekette DEMA'nın gecikmesi neredeyse sıfırdır; bu, tek başına `ema`'nın hiçbir zaman sahip olmadığı bir özelliktir.

## Dikkat edilmesi gerekenler

Gecikmeyi iptal etmek, hareketli ortalamaları başta faydalı kılan yumuşatmanın bir kısmını da iptal eder — DEMA, özellikle kısa uzunluklarda, gerçek dönüşlerde `ema`'dan daha fazla aşırı tepki verir ve savrulur. Ayrıca düz bir EMA'nın kabaca iki katı ısınma süresine ihtiyaç duyar (`EMA2`, zaten ısınmış tam bir `EMA1` penceresi gerektirir).

## Kaynak

Formül kaynağı: [https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/double-exponential-moving-average-dema](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/double-exponential-moving-average-dema)
