# Denge Hacmi (OBV)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/obv.md)

`zeonta.obv()` — Cumulative volume, added on up closes and subtracted on down closes.

## Ne ölçer

Hacmi yönle birleştirmenin en eski ve en basit yolu: fiyat yukarı kapandığında barın hacmini ekle, aşağı kapandığında çıkar ve kümülatif bir toplam tut. Arkasındaki fikir — hacim fiyatı öncüler — OBV ile fiyat arasındaki [divergence](divergence.md)'in yakalamak üzere kurulduğu şeydir.

## Formül

```text
Kapanış > Önceki Kapanış ise: OBV = Önceki OBV + Hacim; Kapanış < Önceki Kapanış ise: OBV = Önceki OBV - Hacim; Kapanış = Önceki Kapanış ise: OBV = Önceki OBV (değişmez)
```

## Parametreler

**Gerekli girdiler:** `close`, `volume`

_Yok._

## Döndürdükleri

| Kolon |
| --- |
| `OBV` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.obv(df['close'], df['volume']).tail(3)
```

```text
date
2024-10-25    4756931.0
2024-10-26    4386817.0
2024-10-27    4123862.0
Name: OBV, dtype: float64
```

**Accessor biçimi:** `df.zta.obv(...)`

## Nasıl okunur

Mutlak seviyenin hiçbir anlamı yoktur (tamamen kümülatif toplamın nereden başladığına bağlıdır); önemli olan eğimi ve bu eğimin fiyatın eğimiyle uyuşup uyuşmadığıdır. Fiyat yatay ya da düşerken OBV'nin yükselmesi, yüzeyin altında birikim oluştuğu şeklinde okunur — klasik boğa uyumsuzluğu.

## Dikkat edilmesi gerekenler

OBV, barın gerçekte gün içinde nasıl işlem gördüğünü göz ardı ederek her barın tüm hacmini yalnızca kapanışa bakarak ya tamamen boğa ya da tamamen ayı sayar — düşükten açılıp yükseğe fırlayan ve marjinal bir yükselişle kapanan bir bar bile %100 alım hacmi sayılır. [cmf](cmf.md) bunun yerine barın tüm aralığını kullanır ve bu noktada daha az kabadır.

## Kaynak

Formül kaynağı: [https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/on-balance-volume-obv](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/on-balance-volume-obv)
