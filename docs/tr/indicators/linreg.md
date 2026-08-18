# Doğrusal Regresyon Eğimi ve Tahmini

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/linreg.md)

`zeonta.linreg()` — Linear regression fit over the window: its slope and its endpoint (forecast) value.

## Ne ölçer

StockCharts bunları iki ayrı indikatör olarak belgeler — Eğim (varsayılan 20) ve Doğrusal Regresyon Tahmini (varsayılan 14) — ama ikisi de bu kütüphanenin `trend_channel` ve `squeeze` içinde zaten hesapladığı tam olarak aynı regresyon uydurmasından gelir; bu yüzden burada tek bir çağrıdan gelen, tek bir uzunluk parametresini paylaşan iki sütun olarak sunulur — birleşik bir `LINEARREG` indikatör ailesine sahip çoğu platformun kullandığı kurala uygun olarak.

## Formül

```text
Son n kapanışa en küçük kareler yöntemiyle y = mx + b doğrusu uydurulur; Eğim = m; Tahmin = uydurulan doğrunun en son bardaki değeri
```

## Parametreler

**Gerekli girdiler:** `close`

| Parametre | Varsayılan |
| --- | --- |
| `length` | `14` |

## Döndürdükleri

| Kolon |
| --- |
| `LRSlope_14` |
| `LRForecast_14` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.linreg(df['close']).tail(3)
```

```text
            LRSlope_14  LRForecast_14
date                                 
2024-10-25   -0.128042      89.925937
2024-10-26   -0.164103      89.551111
2024-10-27   -0.208671      89.073237
```

**Accessor biçimi:** `df.zta.linreg(...)`

## Nasıl okunur

``LRSlope`` herhangi bir trend-gücü ölçütü gibi okunur: işareti yön verir, büyüklüğü diklik verir — tamamen farklı bir açıdan trend okuyan `~zeonta.aroon` ile doğrudan karşılaştırılabilir. ``LRForecast``, yumuşatılmış bir hareketli ortalama gibi fiyatı yakından takip eder, ama düz bir çizgi uydurduğu için (son barları daha ağır tartmak yerine) keskin bir dönüşte daha az aşırı tepki verir.

## Dikkat edilmesi gerekenler

"Tahmin" (Forecast) adı çizginin ne temsil ettiğini anlatır (StockCharts'ın kendi adlandırması), gelecek hakkında bir iddia değildir: ``LRForecast``, ötesine bir projeksiyon değil, *geçerli*, zaten bilinen bardaki uydurulmuş değerdir — bunu gerçek bir fiyat tahmini olarak kullanmak, adın yanlış okunmasıdır.

## Kaynak

Formül kaynağı: [https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/linear-regression-forecast](https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/linear-regression-forecast)
