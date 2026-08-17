# Üssel Hareketli Ortalama (EMA)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/ema.md)

`zeonta.ema()` — Exponentially weighted average that reacts faster to recent closes.

## Ne ölçer

EMA, SMA'nın en büyük tuhaflığını giderir: penceredeki her barın eşit sayılıp sonra aniden düşmesi yerine, ağırlık geçmişe doğru yumuşakça azalır. Son barlar en çok önemlidir, eskiler ise uçurumdan düşmek yerine solar.

## Formül

```text
Bugünkü EMA(n) = Kapanış x k + dünkü EMA(n) x (1 - k), burada k = 2 / (n + 1). Tohum değeri: ilk uygun bardaki EMA(n) = ilk n kapanışın SMA(n)'i.
```

## Parametreler

**Gerekli girdiler:** `close`

| Parametre | Varsayılan |
| --- | --- |
| `length` | `20` |

## Döndürdükleri

| Kolon |
| --- |
| `EMA_20` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.ema(df['close'], length=20).tail(3)
```

```text
date
2024-10-25    90.721181
2024-10-26    90.568592
2024-10-27    90.369888
Name: EMA_20, dtype: float64
```

**Accessor biçimi:** `df.zta.ema(...)`

## Nasıl okunur

Tam olarak bir SMA gibi okuyun, ancak daha erken döneceğini bekleyin. Hızlı ve yavaş EMA arasındaki fark MACD'nin temelidir; artan uzunlukta üst üste dizilmiş EMA'lar ise şeridi (ribbon) oluşturur.

## Dikkat edilmesi gerekenler

Daha hızlı tepki, daha çok yanlış dönüş demektir — EMA, bir SMA'nın yumuşatıp geçeceği tek barlık sıçramaya tepki verir. Ayrıca farklı platformlar özyinelemeyi farklı tohumlarla başlatır; bu kütüphane ilk n kapanışın SMA'i ile başlatır, dolayısıyla ilk birkaç değer yalnızca ilk kapanıştan başlatan bir grafikle uyuşmayabilir.
