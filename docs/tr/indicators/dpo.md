# Trendi Arındırılmış Fiyat Osilatörü (DPO)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/dpo.md)

`zeonta.dpo()` — Price from n/2+1 bars ago minus the current n-bar SMA, built to expose cycles.

## Ne ölçer

Bu kütüphanedeki diğer her osilatör *geçerli* fiyatı bir hareketli ortalamayla ya da önceki bir değerle karşılaştırır; DPO bunun yerine *eski* bir fiyatı *geçerli* SMA ile karşılaştırır. Bu tersine çevirme bilinçlidir — trend bileşenini kaldırır, böylece kalan salınım piyasanın gerçek döngü tepe ve dipleriyle örtüşür; bedeli ise çizginin en son barlara artık hiç tepki vermemesidir.

## Formül

```text
DPO = Kapanış[n/2 + 1 bar önce] - SMA(Kapanış, n)
```

## Parametreler

**Gerekli girdiler:** `close`

| Parametre | Varsayılan |
| --- | --- |
| `length` | `20` |

## Döndürdükleri

| Kolon |
| --- |
| `DPO_20` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.dpo(df['close']).tail(3)
```

```text
date
2024-10-25    0.245810
2024-10-26    1.671405
2024-10-27    1.352820
Name: DPO_20, dtype: float64
```

**Accessor biçimi:** `df.zta.dpo(...)`

## Nasıl okunur

Baskın döngü uzunluğunu tahmin etmek için ardışık DPO tepeleri (ya da dipleri) arasındaki bar sayısını sayın, sonra bu tahmini diğer araçların uzunluklarını ayarlamak için kullanın. Bu bir döngü-belirleme aracıdır, momentum ya da trend sinyali değildir — `macd` ya da `rsi` gibi okunmamalıdır.

## Dikkat edilmesi gerekenler

Bilinçli olarak sola kaydırıldığından (eski bir fiyat kullanır), en son DPO değeri en son barları yansıtmaz — tasarım gereği gecikir ve bir grafikte saf bakışla göründüğü gibi gerçek zamanlı bir sinyal için kullanılamaz.

## Kaynak

Formül kaynağı: [https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/detrended-price-oscillator-dpo](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/detrended-price-oscillator-dpo)
