# Laguerre RSI

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/laguerre_rsi.md)

`zeonta.laguerre_rsi()` — RSI computed over a 4-stage Laguerre filter instead of Wilder smoothing.

## Ne ölçer

John Ehlers'ın [rsi](rsi.md)'ye hızlı-tepki veren alternatifi: Wilder'ın özyinelemesiyle yumuşatılmış tam bir geriye-bakış penceresi yerine, bu, fiyatı 4 aşamalı bir tüm-geçiren filtre kademesinden (düşük-frekans bileşenlerini yüksek-frekans olanlardan daha fazla geciktiren bir 'zaman bükmesi') geçirir ve momentumu dört aşama arasındaki ilişkilerden okur.

## Formül

```text
4 aşamalı Laguerre filtresi (L0..L3) Wilder yumuşatmasının yerini alır; aşamadan-aşamaya farklardan CU/CD; LRSI = CU/(CU+CD)
```

## Parametreler

**Gerekli girdiler:** `close`

| Parametre | Varsayılan |
| --- | --- |
| `gamma` | `0.5` |

## Döndürdükleri

| Kolon |
| --- |
| `LRSI_0.5` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.laguerre_rsi(df['close']).tail(3)
```

```text
date
2024-10-25    0.000000
2024-10-26    0.182379
2024-10-27    0.002458
Name: LRSI_0.5, dtype: float64
```

**Accessor biçimi:** `df.zta.laguerre_rsi(...)`

## Nasıl okunur

RSI ile aynı 0-1 ölçeği ve aşırı-alım/aşırı-satım sezgisi (Ehlers'in kendi örneği %20/%80 seviyelerini kullanır), ama çok daha hızlı tepki vermesi ve ortada sürüklenmek yerine genellikle uçlara yapışmasıyla bilinir.

## Dikkat edilmesi gerekenler

Filtre sıfır bir başlangıç durumundan başlar, bu yüzden ilk birkaç bar anlamlı bir okuma değil, bir ısınma geçişidir — pencereli bir indikatörün sahip olduğu sabit bir ısınma uzunluğu yoktur, çünkü filtrenin kendi belleği hiçbir zaman tamamen temizlenmez, yalnızca söner.

## Kaynak

Formül kaynağı: [https://www.mesasoftware.com/papers/TimeWarp.pdf](https://www.mesasoftware.com/papers/TimeWarp.pdf)
