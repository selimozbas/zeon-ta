# Değişken Endeks Dinamik Ortalaması (VIDYA)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/vidya.md)

`zeonta.vidya()` — An EMA whose smoothing speed adapts bar by bar to CMO's momentum reading.

## Ne ölçer

Düzleştirme sabiti sabit kalmak yerine [cmo](cmo.md)'nun momentum okumasıyla ölçeklenen bir [ema](ema.md) — momentum zayıf ve çalkantılıyken `0`'a doğru donar (hiç güncelleme yapılmaz), momentum güçlü şekilde tek yönlüyken tam EMA sabitine doğru açılır. [kama](kama.md)'nın Verimlilik Oranı'ndan farklı bir kendi kendine ayarlanma fikri, ama aynı temel motivasyon: her piyasa koşulu için tek bir sabit hız kullanma.

## Formül

```text
VIDYA = Kapanış * F * |CMO/100| + VIDYA[-1] * (1 - F * |CMO/100|), F = 2/(length+1)
```

## Parametreler

**Gerekli girdiler:** `close`

| Parametre | Varsayılan |
| --- | --- |
| `length` | `14` |
| `cmo_length` | `9` |

## Döndürdükleri

| Kolon |
| --- |
| `VIDYA_14_9` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.vidya(df['close']).tail(3)
```

```text
date
2024-10-25    91.395668
2024-10-26    91.266282
2024-10-27    91.057410
Name: VIDYA_14_9, dtype: float64
```

**Accessor biçimi:** `df.zta.vidya(...)`

## Nasıl okunur

Herhangi bir hareketli ortalama gibi okunur — fiyatın üstünden geçmesi ya da kendi eğimi.

## Dikkat edilmesi gerekenler

İkisi de sonucu anlamlı şekilde değiştiren, üst üste iki parametre (temel EMA hızı için `length`, onu yönlendiren momentum okuması için `cmo_length`) — `ema`'nın olduğu gibi tek-düğmeli bir indikatör değil.

## Kaynak

Formül kaynağı: [https://www.tradingpedia.com/forex-trading-indicators/chandes-variable-index-dynamic-average/](https://www.tradingpedia.com/forex-trading-indicators/chandes-variable-index-dynamic-average/)
