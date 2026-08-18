# Anlık Trend Çizgisi (Ehlers)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/instantaneous_trendline.md)

`zeonta.instantaneous_trendline()` — Ehlers' Instantaneous Trendline: a filter tuned to track the trend, not the cycle.

## Ne ölçer

Ehlers bu ikinci dereceden filtreyi, fiyatın *döngüsel* bileşenini reddederken *trend* bileşenini takip etmek için özel olarak tasarladı — sıradan bir hareketli ortalama ikisini birlikte geçirir, gecikmesinin nedeni de budur: o gecikmenin bir kısmı, hiçbir zaman trend olmamış bir döngüyü düzleştirmeye harcanır. `super_smoother` genel amaçlı bir alçak geçiren filtreyken, bu özellikle trendi izole etmek için tasarlanmıştır.

## Formül

```text
IT = (a - a^2/4) x Kapanış + 0,5 x a^2 x Kapanış[t-1] - (a - 0,75 x a^2) x Kapanış[t-2] + 2 x (1-a) x IT[t-1] - (1-a)^2 x IT[t-2]
```

## Parametreler

**Gerekli girdiler:** `close`

| Parametre | Varsayılan |
| --- | --- |
| `alpha` | `0.07` |

## Döndürdükleri

| Kolon |
| --- |
| `ITREND_0.07` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.instantaneous_trendline(df['close']).tail(3)
```

```text
date
2024-10-25    90.275484
2024-10-26    90.138468
2024-10-27    89.906359
Name: ITREND_0.07, dtype: float64
```

**Accessor biçimi:** `df.zta.instantaneous_trendline(...)`

## Nasıl okunur

`super_smoother`'a ya da bir EMA'ya benzer ruhta, yumuşatılmış bir trend çizgisi olarak okuyun; ama döngüsel, aralıkta sıkışmış bir dönem boyunca okumanın gerçekten daha düz olmasını bekleyin — çünkü bu filtrenin reddetmek üzere tasarlandığı bileşen tam olarak budur.

## Dikkat edilmesi gerekenler

Bu kütüphanedeki diğer çoğu filtrenin aksine bar-sayısı bir uzunluk yerine doğrudan ``alpha`` ile parametrelenir (Ehlers'in kendi varsayılanı ``0.07``'dir) — uzunluk tabanlı bir sarmalayıcı bazı platformların eklediği doğal bir genişletme olsa da, birincil kaynağın kendisi ``alpha`` kullanır, bu yüzden bu uygulama da onu sunar.

## Kaynak

Formül kaynağı: [https://www.tradingview.com/support/solutions/43000589152-instantaneous-trendline/](https://www.tradingview.com/support/solutions/43000589152-instantaneous-trendline/)
