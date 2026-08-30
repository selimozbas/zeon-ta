# Kütle Endeksi

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/mass_index.md)

`zeonta.mass_index()` — Range-expansion measure built to flag reversals, from EMA-of-EMA ratio of the range.

## Ne ölçer

Donald Dorsey bunu tamamen bar-başı *aralıktan* inşa etti, fiyat yönünden değil: bir EMA, o EMA'nın EMA'sından daha hızlı tepki verir, bu yüzden aralık genişledikçe oranları büyür — bu genişleme yukarı bir hareketten mi aşağı bir hareketten mi geldiği fark etmez. Dorsey'in kendi savı, bu aralık genişlemesinin bir trend dönüşünden önce ortaya çıkma eğiliminde olduğuydu, dönüşün hangi yöne olacağını söylemeden.

## Formül

```text
TekEMA = EMA(Yüksek-Düşük, ema_length); ÇiftEMA = EMA(TekEMA, ema_length); Oran = TekEMA/ÇiftEMA; MASS = Toplam(Oran, sum_length)
```

## Parametreler

**Gerekli girdiler:** `high`, `low`

| Parametre | Varsayılan |
| --- | --- |
| `ema_length` | `9` |
| `sum_length` | `25` |

## Döndürdükleri

| Kolon |
| --- |
| `MASS_9_25` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.mass_index(df['high'], df['low']).tail(3)
```

```text
date
2024-10-25    27.912747
2024-10-26    27.761708
2024-10-27    27.669469
Name: MASS_9_25, dtype: float64
```

**Accessor biçimi:** `df.zta.mass_index(...)`

## Nasıl okunur

Dorsey'in kendi 'dönüş şişkinliği' eşiği, 27 okumasının ardından 26,5'in altına geri düşmesidir — bu kütüphanedeki çoğu indikatörün çalıştığı gibi bir sıfır-çizgisi geçişi ya da sınırlı bir osilatör değil, izlenecek belirli bir seviye desenidir.

## Dikkat edilmesi gerekenler

Yapısı gereği sıradan koşullarda 20'lerin ortasında okunur (1'e yakın gezinen bir oranın 25-barlık toplamıdır), bu yüzden 0/50/100 tarzı bir sezgi yerine kendi belirli eşiğine ihtiyaç duyar.

## Kaynak

Formül kaynağı: [https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/mass-index](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/mass-index)
