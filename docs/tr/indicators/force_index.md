# Force Index (Güç Endeksi)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/force_index.md)

`zeonta.force_index()` — Volume-weighted price change: Elder's Force Index.

## Ne ölçer

Alexander Elder'ın fiyat yönü, fiyat büyüklüğü ve hacmi tek bir çizgide birleştirmesi — daha fazla hacimle daha uzağa hareket eden bir bar, aynı hareketin düşük hacimde yaptığından orantılı olarak daha büyük bir okuma üretir; bu, `momentum` gibi saf bir fiyat indikatörünün göremeyeceği bir şeydir. `elder_ray` ile aynı yazarın indikatörüdür; alım-satım baskısını fiyatın bir EMA'ya göre konumu yerine hacim üzerinden görür.

## Formül

```text
FI(1) = (Kapanış - ÖncekiKapanış) x Hacim; FI(n) = EMA(FI(1), n)
```

## Parametreler

**Gerekli girdiler:** `close`, `volume`

| Parametre | Varsayılan |
| --- | --- |
| `length` | `13` |

## Döndürdükleri

| Kolon |
| --- |
| `FI_13` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.force_index(df['close'], df['volume']).tail(3)
```

```text
date
2024-10-25    -79964.843100
2024-10-26   -120209.208486
2024-10-27   -126957.856416
Name: FI_13, dtype: float64
```

**Accessor biçimi:** `df.zta.force_index(...)`

## Nasıl okunur

Yükselen bir Force Index bir yükseliş trendini doğrular (fiyat güçlü hacimle ilerliyor); bir yükseliş trendi sırasında düşen bir Force Index, ya da fiyata karşı ayı uyumsuzluğu, yükselişin inandırıcılığını kaybettiğini işaret eder. Elder'ın kendisi giriş zamanlaması için hem kısa, yumuşatılmamış bir versiyon (``length=1`` ya da 2) hem de altta yatan trend için yumuşatılmış 13-periyotluk versiyonu kullandı.

## Dikkat edilmesi gerekenler

`obv` ve `adl` gibi, yalnızca işareti ve eğimi anlamlıdır — mutlak seviye, menkul kıymetin kendi tipik hacmiyle doğrudan ölçeklenir, bu yüzden farklı semboller arasında karşılaştırılamaz.

## Kaynak

Formül kaynağı: [https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/force-index](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/force-index)
