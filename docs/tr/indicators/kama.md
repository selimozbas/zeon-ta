# Kaufman Uyarlanabilir Hareketli Ortalama (KAMA)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/kama.md)

`zeonta.kama()` — Adapts its own smoothing to how efficiently price is trending.

## Ne ölçer

Sabit uzunluklu her hareketli ortalama bir uzlaşmadır: gerçek hareketleri yakalayacak kadar kısa, gürültüyü göz ardı edecek kadar uzun ve ayarlanmadığı rejim için yanlış. KAMA bu ödünleşmeyi, fiyatın ne kadar verimli trend yaptığını (Verimlilik Oranı) bar bar ölçüp kendi hızını hızlı ile yavaş bir EMA arasında otomatik olarak kaydırarak aşar.

## Formül

```text
Verimlilik Oranı ER = |Kapanış - n periyot önceki Kapanış| / Toplam(|Kapanış - Önceki Kapanış|, n); Yumuşatma Sabiti SC = [ER x (en hızlı SC - en yavaş SC) + en yavaş SC]^2, burada en hızlı SC = 2/(hızlı+1) ve en yavaş SC = 2/(yavaş+1); KAMA = Önceki KAMA + SC x (Kapanış - Önceki KAMA)
```

## Parametreler

**Gerekli girdiler:** `close`

| Parametre | Varsayılan |
| --- | --- |
| `length` | `10` |
| `fast` | `2` |
| `slow` | `30` |

## Döndürdükleri

| Kolon |
| --- |
| `KAMA_10_2_30` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.kama(df['close'], length=10, fast=2, slow=30).tail(3)
```

```text
date
2024-10-25    91.133245
2024-10-26    90.873663
2024-10-27    90.563219
Name: KAMA_10_2_30, dtype: float64
```

**Accessor biçimi:** `df.zta.kama(...)`

## Nasıl okunur

Tam olarak diğer hareketli ortalamalar gibi okuyun — trend yönü, destek/direnç, kesişimler — ama bir rejim değişimi sırasında ona daha çok güvenin: temiz bir trend başladığında kendiliğinden fiyata yapışır, piyasa dalgalandığında ise siz bir uzunluk yeniden ayarlamadan kendiliğinden düzleşir.

## Dikkat edilmesi gerekenler

KAMA yine de tepkiseldir, öngörücü değil — bir rejim değişimine, fiyat zaten farklı hareket etmeye başladıktan sonra uyum sağlar; bu, her hareketli ortalamanın taşıdığı aynı gecikmedir, sadece kendini ayarlayan bir uzunlukla. Verimlilik Oranı'nın kendisi kısa pencerelerde gürültülüdür, bu yüzden çok küçük `length` değerleri KAMA'nın hızının neredeyse fiyat kadar sıçramasına yol açabilir.

## Kaynak

Formül kaynağı: [https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/kaufmans-adaptive-moving-average-kama](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/kaufmans-adaptive-moving-average-kama)
