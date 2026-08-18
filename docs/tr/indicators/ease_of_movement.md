# Hareket Kolaylığı (EMV)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/ease_of_movement.md)

`zeonta.ease_of_movement()` — How much price moves per unit of volume — Arms' Ease of Movement.

## Ne ölçer

Richard Arms'ın kutu-oranı fikri, bir barın fiyat hareketini o hareketin ne kadar hacme ihtiyaç duyduğuyla doğrudan karşılaştırır — `chaikin_oscillator` ve `mfi`'nin farklı bir açıdan sorduğu aynı temel soru. Düşük hacimde büyük bir fiyat hareketi, yüksek hacimdeki aynı hareketten çok daha yüksek puan alır.

## Formül

```text
KatedilenMesafe = (Yüksek+Düşük)/2 - (ÖncekiYüksek+ÖncekiDüşük)/2; KutuOranı = (Hacim/100.000.000) / (Yüksek-Düşük); EMV(1) = KatedilenMesafe / KutuOranı; EOM = SMA(EMV(1), n)
```

## Parametreler

**Gerekli girdiler:** `high`, `low`, `volume`

| Parametre | Varsayılan |
| --- | --- |
| `length` | `14` |

## Döndürdükleri

| Kolon |
| --- |
| `EOM_14` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.ease_of_movement(df['high'], df['low'], df['volume']).tail(3)
```

```text
date
2024-10-25    24.475105
2024-10-26     6.079390
2024-10-27   -27.581227
Name: EOM_14, dtype: float64
```

**Accessor biçimi:** `df.zta.ease_of_movement(...)`

## Nasıl okunur

Sürekli pozitif okumalar, fiyatın kolayca ilerlediği anlamına gelir — fiyat hareketi birimi başına az hacim gerekir, sağlıklı bir yükseliş trendi. Sıfıra yakın ya da altındaki okumalar, fiyatın hacme karşı hareket etmekte zorlandığı anlamına gelir; ister yatay ister aktif olarak düşüyor olsun.

## Dikkat edilmesi gerekenler

Sıfır-aralıklı bir bar ya da sıfır-hacimli bir bar, kutu oranını dejenere eder (sıfır ya da sonsuz bir payda); bu uygulama her iki durumu da hata vermek ya da ``inf``/``NaN`` üretmek yerine ham EMV'ye ``0`` katkı olarak ele alır — `cmf`'nin Para Akışı Çarpanı'nın kendi sıfır-aralık durumu için kullandığı aynı kural.

## Kaynak

Formül kaynağı: [https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/ease-of-movement-emv](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/ease-of-movement-emv)
