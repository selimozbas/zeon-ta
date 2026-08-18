# TRIX (Üçlü Üssel Ortalama)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/trix.md)

`zeonta.trix()` — 1-bar percent change of a triple-smoothed EMA — momentum with heavy noise filtering.

## Ne ölçer

Bir değişim ölçülmeden önce üç EMA geçişi, `roc`'un eski bir fiyatla tek karşılaştırmasından ya da `macd`'nin tek geçişli EMA farkından bilinçli olarak daha ağır bir filtredir — bu ekstra gürültü azaltmanın bedeli, TRIX'in gerçekten dönmeden önce orantılı olarak daha fazla gecikmedir.

## Formül

```text
EMA1 = EMA(Kapanış, n); EMA2 = EMA(EMA1, n); EMA3 = EMA(EMA2, n); TRIX = (EMA3[t] - EMA3[t-1]) / EMA3[t-1] x 100
```

## Parametreler

**Gerekli girdiler:** `close`

| Parametre | Varsayılan |
| --- | --- |
| `length` | `15` |
| `signal` | `9` |

## Döndürdükleri

| Kolon |
| --- |
| `TRIX_15_9` |
| `TRIXs_15_9` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.trix(df['close']).tail(3)
```

```text
            TRIX_15_9  TRIXs_15_9
date                             
2024-10-25  -0.053222   -0.049919
2024-10-26  -0.056651   -0.051266
2024-10-27  -0.062506   -0.053514
```

**Accessor biçimi:** `df.zta.trix(...)`

## Nasıl okunur

Sıfır çizgisini ve sinyal çizgisini `macd` ile aynı şekilde okuyun: sıfırın üzerine çıkmak boğa, altına inmek ayı sinyalidir; TRIX'in kendi sinyal çizgisini (TRIX'in 9 günlük EMA'sı) yukarı/aşağı kesmesi aynı çağrının daha erken, daha gürültülü bir versiyonunu verir.

## Dikkat edilmesi gerekenler

TRIX'i sakinleştiren üçlü yumuşatma, onu aynı zamanda yavaşlatır — hızlı hareket eden ya da kısa ömürlü bir trendde, hareket zaten bitmişken TRIX hâlâ dönüyor olabilir. Tam da bu yüzden genellikle daha uzun zaman dilimlerinde (haftalık grafikler ya da uzun günlük periyotlar) kullanılır.

## Kaynak

Formül kaynağı: [https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/trix](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-indicators/trix)
