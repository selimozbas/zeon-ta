# Coppock Eğrisi

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/coppock_curve.md)

`zeonta.coppock_curve()` — A WMA of two summed rate-of-change measures, built to spot major long-term bottoms.

## Ne ölçer

Edwin Coppock, iki `roc` periyodunu (14 ve 11) kendi araştırmasında yatırımcı duyarlılığının bir kayıptan toparlanmasının ne kadar sürdüğü etrafında kurdu — teknik bir indikatör için sıra dışı girdiler, ama sonuç yavaş, ağır biçimde yumuşatılmış uzun vadeli bir momentum çizgisi. Yumuşatmadan önce iki `roc` okumasını toplamak, tek başına her iki periyottan da daha geniş bir momentum görüşü verir.

## Formül

```text
Coppock = WMA(ROC(Kapanış, uzun) + ROC(Kapanış, kısa), wma_uzunluk)
```

## Parametreler

**Gerekli girdiler:** `close`

| Parametre | Varsayılan |
| --- | --- |
| `long` | `14` |
| `short` | `11` |
| `wma_length` | `10` |

## Döndürdükleri

| Kolon |
| --- |
| `COPC_14_11_10` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.coppock_curve(df['close']).tail(3)
```

```text
date
2024-10-25   -1.019351
2024-10-26   -1.941507
2024-10-27   -2.904687
Name: COPC_14_11_10, dtype: float64
```

**Accessor biçimi:** `df.zta.coppock_curve(...)`

## Nasıl okunur

Aslında büyük piyasa diplerini çağırmak için aylık grafikler için tasarlandı: bir alım sinyali, Coppock Eğrisi'nin sıfırın altından yukarı dönmesidir. Hiçbir zaman günlük ticaret sinyalleri ya da tepe çağırmak için tasarlanmadı — Coppock onu özellikle uzun vadeli, yalnızca alım tarafı için bir araç olarak inşa etti.

## Dikkat edilmesi gerekenler

Coppock'un kendi (14, 11, 10) ayarlarını (tasarlandığı aylık grafikler yerine) günlük grafiklere uygulamak, artık tasarlandığı büyük-dip-çağıran araç gibi davranmayan, çok daha gürültülü ve hızlı dönen bir çizgi üretir.

## Kaynak

Formül kaynağı: [https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/coppock-curve](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/coppock-curve)
