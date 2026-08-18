# Fisher Dönüşümü (Ehlers)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/fisher_transform.md)

`zeonta.fisher_transform()` — Ehlers' Fisher Transform: normalized price reshaped to sharpen its turning points.

## Ne ölçer

Sıradan fiyat verisi, çoğu istatistiksel aracın sessizce varsaydığı Gauss (çan eğrisi) dağılımı değil, kabaca tekdüze-ile-iki-modlu arası bir dağılıma sahiptir. Ehlers'in içgörüsü, normalize edilmiş bir fiyatı Gauss'a yakın bir şeye dönüştürmekti — bu dönüşüm altında büyük sapmalar sıradan gürültü yerine gerçekten nadir olaylar hâline gelir; bu da dönüşümün dönüş noktalarını doğrudan fiyattan kurulmuş bir osilatörden daha keskin ve kararlı yapan şeydir.

## Formül

```text
Konum = (Fiyat - EnDüşükFiyat(n)) / (EnYüksekFiyat(n) - EnDüşükFiyat(n)) - 0,5; Value1 = 0,33 x 2 x Konum + 0,67 x Value1[t-1], +/-0,999'a sınırlanır; Fish = 0,5 x ln((1 + Value1) / (1 - Value1)) + 0,5 x Fish[t-1]
```

## Parametreler

**Gerekli girdiler:** `high`, `low`

| Parametre | Varsayılan |
| --- | --- |
| `length` | `10` |

## Döndürdükleri

| Kolon |
| --- |
| `FISHERT_10` |
| `FISHERTs_10` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.fisher_transform(df['high'], df['low']).tail(3)
```

```text
            FISHERT_10  FISHERTs_10
date                               
2024-10-25   -0.813408    -0.884008
2024-10-26   -0.951520    -0.813408
2024-10-27   -1.273442    -0.951520
```

**Accessor biçimi:** `df.zta.fisher_transform(...)`

## Nasıl okunur

``FISHERT``/``FISHERTs``'i, `macd`'nin çizgisi ve sinyalinin okunduğu gibi bir kesişim çifti olarak okuyun: Ehlers'in bu dönüşüme kattığı keskinlik, kesişimlerin `macd` gibi yuvarlatılmış bir indikatörün gerisinde kalması yerine gerçek dönüş noktalarında meydana gelme eğiliminde olması anlamına gelir.

## Dikkat edilmesi gerekenler

Keskin, kararlı dönüşler, yakın aralığın kenarına yakın değerleri güçlendirmenin doğrudan bir sonucudur — gerçekten dalgalı, aralıkta sıkışmış bir piyasada bu, daha az ve daha temiz kesişimler yerine daha sık ve daha az anlamlı kesişimler anlamına gelebilir.

## Kaynak

Formül kaynağı: [https://www.mesasoftware.com/papers/UsingTheFisherTransform.pdf](https://www.mesasoftware.com/papers/UsingTheFisherTransform.pdf)
