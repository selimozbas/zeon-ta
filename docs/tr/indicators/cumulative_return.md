# Kümülatif Getiri

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/cumulative_return.md)

`zeonta.cumulative_return()` — Cumulative percentage return since the start of the series.

## Ne ölçer

Bu kütüphanedeki indikatörler arasında tuhaf olanı: diğer her biri yalnızca sabit bir *length* bar geriye bakar, bu yüzden N barındaki değeri, daha sonra önüne ne kadar geçmiş eklerseniz ekleyin sabit kalır. Bu ise verdiğiniz serinin 0. barına sabitlenir — *o* serinin en başından beri süregelen yüzde kâr ya da zarar.

## Formül

```text
CUMRET = (Kapanış[t] / Kapanış[0] - 1) * 100
```

## Parametreler

**Gerekli girdiler:** `close`

_Yok._

## Döndürdükleri

| Kolon |
| --- |
| `CUMRET` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.cumulative_return(df['close']).tail(3)
```

```text
date
2024-10-25    -9.195891
2024-10-26   -10.180769
2024-10-27   -10.822573
Name: CUMRET, dtype: float64
```

**Accessor biçimi:** `df.zta.cumulative_return(...)`

## Nasıl okunur

Bir equity-curve grafiğinin çizdiğiyle aynı şekilde, basit bir süregelen toplam getiri çizgisi — fiyatın 0. bardan beri en çok yükseldiği yerde en yüksek, en çok düştüğü yerde en düşük okunur.

## Dikkat edilmesi gerekenler

Bunu daha uzun bir geçmiş üzerinde yeniden çalıştırmak *her* önceki değeri değiştirir, çünkü sabitleme noktası (0. bar) onunla birlikte hareket eder — bu tasarım gereğidir, çünkü sorulan soru her zaman 'bu serinin başından beri getiri'dir, ama buradaki her diğer indikatörün verdiği aynı kararlılığı bekliyorsanız gerçek bir sürpriz olur.

## Kaynak

Formül kaynağı: [https://en.wikipedia.org/wiki/Rate_of_return](https://en.wikipedia.org/wiki/Rate_of_return)
