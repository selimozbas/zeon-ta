# Değişim Oranı (ROC)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/roc.md)

`zeonta.roc()` — Percentage price change over n bars — the normalised sibling of momentum.

## Ne ölçer

[momentum](momentum.md)'un normalize edilmiş kardeşi: aynı n-bar-önce karşılaştırması, ham fiyat farkı yerine yüzde olarak ifade edilir. Bu tek değişiklik, onu semboller arasında ve aynı sembolün zaman içindeki farklı fiyat seviyeleri arasında karşılaştırılabilir kılar.

## Formül

```text
ROC = [(Kapanış - n periyot önceki Kapanış) / n periyot önceki Kapanış] x 100
```

## Parametreler

**Gerekli girdiler:** `close`

| Parametre | Varsayılan |
| --- | --- |
| `length` | `12` |

## Döndürdükleri

| Kolon |
| --- |
| `ROC_12` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.roc(df['close'], length=12).tail(3)
```

```text
date
2024-10-25   -1.119992
2024-10-26   -2.012009
2024-10-27   -4.132452
Name: ROC_12, dtype: float64
```

**Accessor biçimi:** `df.zta.roc(...)`

## Nasıl okunur

ROC, tıpkı Momentum gibi sıfır etrafında salınır; ancak "+5" okuması her zaman aynı şeyi ifade eder — pencere boyunca %5'lik bir yükseliş — sembol 10 dolardan da işlem görse 10.000 dolardan da. Sıfırdan sert sapmalar, enstrümanın kendi son dönem hızına göre olağandışı hızlı hareketleri işaret eder.

## Dikkat edilmesi gerekenler

ROC, n bar önceki fiyata böler; bu yüzden referans kapanışın tam olarak sıfır olduğu herhangi bir barda tanımsızdır (`NaN` döner) — fiyat yerine bir spread ya da oran olarak kote edilen enstrümanlarda gerçek bir olasılıktır. Ayrıca Momentum'un yatay banttaki testere davranışını da devralır: arkasında kalıcı bir trend olmayan hızlı bir salınım.

## Kaynak

Formül kaynağı: [https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/rate-of-change-roc](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/rate-of-change-roc)
