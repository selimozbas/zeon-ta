# Hull Hareketli Ortalaması (HMA)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/hma.md)

`zeonta.hma()` — Fast-turning WMA-of-WMAs designed to cut lag without adding noise.

## Ne ölçer

Tek başına `wma`, `sma`'ya kıyasla gecikmeyi yalnızca ölçülü biçimde azaltır. Hull'un içgörüsü şu: hızlı bir yarı-uzunluk WMA alıp iki katına çıkarın, tam-uzunluk WMA'yı çıkarın — bu, hızlı WMA'nın yanında sadece ortalama almak yerine onun *ilerisine* ekstrapolasyon yapar. Bu ekstrapolasyon tek başına oynaktır, bu yüzden bir kısa WMA daha onu gerçekten hızlı ama yine de düzgün bir çizgiye dönüştürür.

## Formül

```text
Ham = (2 x WMA(Kapanış, Integer(n/2))) - WMA(Kapanış, n); HMA = WMA(Ham, Integer(sqrt(n))) — Alan Hull'un kendi formülüne göre her iki ara uzunluk da sıfıra doğru kesilir (truncate), en yakın tam sayıya yuvarlanmaz
```

## Parametreler

**Gerekli girdiler:** `close`

| Parametre | Varsayılan |
| --- | --- |
| `length` | `20` |

## Döndürdükleri

| Kolon |
| --- |
| `HMA_20` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.hma(df['close'], length=20).tail(3)
```

```text
date
2024-10-25    90.055085
2024-10-26    89.841562
2024-10-27    89.517649
Name: HMA_20, dtype: float64
```

**Accessor biçimi:** `df.zta.hma(...)`

## Nasıl okunur

Diğer hareketli ortalamalar gibi okuyun, ama aynı uzunlukta `sma`, `ema` ya da düz `wma`'dan çok daha yakından fiyata yapışmasını bekleyin — ve keskin bir dönüşte yerleşmeden önce zaman zaman aşırı tepki vermesini de; bu, ekstrapolasyon adımının doğrudan bir sonucudur.

## Dikkat edilmesi gerekenler

Gecikmeyi azaltan aynı ekstrapolasyon, HMA'nın keskin bir dönüşte gerçek dönüş noktasının ötesine geçebileceği, düzelmeden önce kısa süreliğine yanlış yönü gösterebileceği anlamına da gelir — sadece geride kalan ve asla aşırı tepki vermeyen `sma`/`wma`'nın aksine. Ayrıca bu kütüphanedeki en hesaplama yoğun hareketli ortalamadır (bar başına üç WMA geçişi). Bazı ikincil kaynaklar iki ara uzunluğu kesme yerine yuvarlama olarak tarif eder; bu uygulama Alan Hull'un kendi formülünü (kesme) izler — hem kendi sitesine karşı hem de canlı bir TradingView okumasına karşı ampirik olarak doğrulanmıştır.

## Kaynak

Formül kaynağı: [https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/hull-moving-average-hma](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/hull-moving-average-hma)
