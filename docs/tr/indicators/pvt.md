# Fiyat Hacim Trendi (PVT)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/pvt.md)

`zeonta.pvt()` — Running total of volume-scaled percentage price change.

## Ne ölçer

[obv](obv.md)'nin daha kademeli kuzeni: OBV, kapanışın yalnızca hangi yöne hareket ettiğine göre bir barın *tüm* hacmini ekler; PVT ise eklediği hacmi kapanışın yüzde olarak *ne kadar* hareket ettiğine göre ölçeklendirir, böylece %3'lük bir yukarı gün, %1'lik bir yukarı günün üç katı katkı sağlar, ikisinde de aynı tam hacim yerine.

## Formül

```text
PVT[0] = 0; PVT[i] = PVT[i-1] + Hacim[i] * (Kapanış[i] - Kapanış[i-1]) / Kapanış[i-1]
```

## Parametreler

**Gerekli girdiler:** `close`, `volume`

_Yok._

## Döndürdükleri

| Kolon |
| --- |
| `PVT` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.pvt(df['close'], df['volume']).tail(3)
```

```text
date
2024-10-25   -59713.678888
2024-10-26   -63728.003586
2024-10-27   -65606.949086
Name: PVT, dtype: float64
```

**Accessor biçimi:** `df.zta.pvt(...)`

## Nasıl okunur

OBV ile aynı şekilde okunur — yükselen fiyatla birlikte yükselen bir çizgi, arkasında gerçek katılım olan trendi doğrular; fiyatla birlikte yeni bir zirve yapamayan bir PVT, klasik bir düşüş yönlü uyumsuzluk uyarısıdır.

## Dikkat edilmesi gerekenler

`obv`/`adl` gibi keyfi bir başlangıç seviyesine sahip süregelen bir toplam — yalnızca eğimi ve fiyattan sapması anlam taşır, mutlak değeri asla.

## Kaynak

Formül kaynağı: [https://www.tradingview.com/support/solutions/43000502345-price-volume-trend-pvt/](https://www.tradingview.com/support/solutions/43000502345-price-volume-trend-pvt/)
