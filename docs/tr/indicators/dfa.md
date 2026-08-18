# Trendi Arındırılmış Dalgalanma Analizi (DFA)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/dfa.md)

`zeonta.dfa()` — Detrended Fluctuation Analysis: a scaling exponent for persistence, robust to trends.

## Ne ölçer

Peng ve ark. (1994), DNA dizilerindeki uzun-menzilli korelasyonları, dizinin kendi yerel trendlerine kanmadan tespit etmek için DFA'yı geliştirdi — bu, bir fiyat serisinin sahip olduğu aynı durağan-olmama sorunudur. hurst_exponent'in klasik (1951) R/S analizinin tahmin ettiği aynı temel niceliği, aynı yuvarlanan log getiri penceresinden tahmin eder, ama pencerenin zaten trendden arındırılmış olduğunu varsaymak yerine, dalgalanmayı ölçmeden önce her kutudan açıkça yerel bir doğrusal trendi çıkararak.

## Formül

```text
profile = cumsum(log_getiri_penceresi - ortalama(log_getiri_penceresi)); her kutu boyutu n için: profile'ı n uzunluğunda örtüşmeyen kutulara böl, her birini yerel bir doğrusal uyumla arındır, kare artıkları F(n) = sqrt(ortalama(artık^2))'de topla; DFA = log(F(n))'nin log(n)'e karşı regresyonunun eğimi
```

## Parametreler

**Gerekli girdiler:** `close`

| Parametre | Varsayılan |
| --- | --- |
| `window` | `100` |

## Döndürdükleri

| Kolon |
| --- |
| `DFA_100` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.dfa(df['close']).tail(3)
```

```text
date
2024-10-25    0.492814
2024-10-26    0.481514
2024-10-27    0.584808
Name: DFA_100, dtype: float64
```

**Accessor biçimi:** `df.zta.dfa(...)`

## Nasıl okunur

hurst_exponent ile aynı ölçek: ``alpha ~= 0,5`` rastgele yürüyüş, ``alpha > 0,5`` kalıcı/trend, ``alpha < 0,5`` kalıcı-olmayan/ortalamaya dönüş. DFA her kutuyu açıkça arındırdığı için, pencere içindeki gerçek bir trend ya da rejim değişikliğinde güvenilir kalır — R/S analizinin yalnızca o trend tarafından yanıltılabileceği bir durum. İki indikatörü aynı seride karşılaştırmak, tam olarak aralarında görüş ayrılığı olabilecek anlarda değerlidir.

## Dikkat edilmesi gerekenler

Bu DFA1'dir (doğrusal yerel arındırma) — daha yüksek dereceli varyantlar da vardır (DFA2, DFA3, ikinci/üçüncü dereceden yerel uyumlar) ve aynı veride farklı sonuç verebilirler; bu yüzden bunu yöntemin belirli, standart bir derecesi olarak ele alın — hurst_exponent'in kendi docstring'inin R/S'e karşı diğer Hurst tahmin edicileri için verdiği aynı uyarı. hurst_exponent gibi, bu da birden fazla kutu boyutu üzerinden her barda yuvarlanan bir regresyondur, tek bir vektörleştirilmiş geçiş değil — büyük bir geçmiş üzerinde kullanmadan önce kendi verinizde ölçün (bkz. `BENCHMARKS.md`).

## Kaynak

Formül kaynağı: [https://doi.org/10.1103/PhysRevE.49.1685](https://doi.org/10.1103/PhysRevE.49.1685)
