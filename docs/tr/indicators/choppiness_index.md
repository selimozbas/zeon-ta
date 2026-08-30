# Sıkışma Endeksi (CHOP)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/choppiness_index.md)

`zeonta.choppiness_index()` — How much a window's price range came from many small moves versus one big one.

## Ne ölçer

E.W. Dreiss, aynı pencerenin hareketini ölçmenin iki yolunu karşılaştırır: her bir barın kendi aralığını topla (fiyat pencere boyunca ileri geri gidip geliyorsa bu çok olur), buna karşılık pencerenin baştan sona ölçülen aralığı (tüm o gidip gelmeler birbirini götürdüyse bu küçük olur). İkisi arasındaki yüksek bir oran, hareketin çoğunun boşa gittiği; 1'e yakın bir oran ise pencerenin her barının aynı yönde net ilerlemeye katkıda bulunduğu anlamına gelir.

## Formül

```text
CHOP = 100 * log10(Toplam(GerçekAralık, n) / (EnYüksekYüksek(n) - EnDüşükDüşük(n))) / log10(n)
```

## Parametreler

**Gerekli girdiler:** `high`, `low`, `close`

| Parametre | Varsayılan |
| --- | --- |
| `length` | `14` |

## Döndürdükleri

| Kolon |
| --- |
| `CHOP_14` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.choppiness_index(df['high'], df['low'], df['close']).tail(3)
```

```text
date
2024-10-25    59.636167
2024-10-26    60.407122
2024-10-27    54.470928
Name: CHOP_14, dtype: float64
```

**Accessor biçimi:** `df.zta.choppiness_index(...)`

## Nasıl okunur

Dreiss'in kendi yaygın olarak atıf yapılan okuması: `61,8`'in üstü konsolidasyonu, `38,2`'nin altı ise temiz bir trendi düşündürür (Fibonacci sayıları formülden türetilmemiş, alışkanlık için seçilmiştir). Yapısı gereği `[0, 100]` ile sınırlıdır, ama bir trendin *hangi* yönde gittiği konusunda hiçbir şey söylemez — `atr`'nin taşıdığı aynı uyarı.

## Dikkat edilmesi gerekenler

Tamamen düz bir pencerede (hem pay hem payda `0`'a çöker), tanımsız bir bölüm ya da yanıltıcı bir sayı yerine `NaN` olur.

## Kaynak

Formül kaynağı: [https://www.tradingview.com/support/solutions/43000501980-choppiness-index-chop/](https://www.tradingview.com/support/solutions/43000501980-choppiness-index-chop/)
