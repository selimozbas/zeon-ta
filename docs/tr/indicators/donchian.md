# Donchian Kanalları

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/donchian.md)

`zeonta.donchian()` — Highest high and lowest low over n bars — the classic breakout channel.

## Ne ölçer

Var olan en basit kanal: son n barın en yüksek zirvesi ve en düşük dibi. Basitliği işin özüdür — orijinal Kaplumbağa Ticareti (Turtle Trading) sistemi neredeyse tamamen bu kanalın kırılımları üzerine kurulmuştu.

## Formül

```text
Üst Kanal = En Yüksek(n); Alt Kanal = En Düşük(n); Orta Çizgi = (Üst Kanal + Alt Kanal) / 2
```

## Parametreler

**Gerekli girdiler:** `high`, `low`

| Parametre | Varsayılan |
| --- | --- |
| `length` | `20` |

## Döndürdükleri

| Kolon |
| --- |
| `DCL_20` |
| `DCM_20` |
| `DCU_20` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.donchian(df['high'], df['low'], length=20).tail(3)
```

```text
             DCL_20    DCM_20   DCU_20
date                                  
2024-10-25  88.9268  90.94945  92.9721
2024-10-26  88.9268  90.94945  92.9721
2024-10-27  88.0724  90.52225  92.9721
```

**Accessor biçimi:** `df.zta.donchian(...)`

## Nasıl okunur

Üst kanaldaki bir kapanış, bu barın son n barın en yüksek zirvesini yaptığı anlamına gelir — bu ifadenin kendisi kırılım sinyalidir. Orta çizgi, kırılımla girilen bir pozisyon için yaygın bir çıkıştır.

## Dikkat edilmesi gerekenler

Kanal mevcut barı da içerir, dolayısıyla fiyat asla kanalın dışında kapanamaz — "fiyat kanalı yukarı kırdı" aslında "fiyat kanala ulaştı" demektir. Kıran barın kendisini dışlayan bir kırılım istiyorsanız önceki barın kanalıyla karşılaştırın.
