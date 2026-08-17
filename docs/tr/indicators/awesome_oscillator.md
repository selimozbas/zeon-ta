# Awesome Osilatör (AO)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/awesome_oscillator.md)

`zeonta.awesome_oscillator()` — Momentum from the gap between a fast and slow SMA of the bar's own midpoint.

## Ne ölçer

Bill Williams'ın momentum okuması, `macd` ile aynı "hızlı HO eksi yavaş HO" şeklinden kurulur, ama iki farkla: kapanış yerine barın kendi orta noktasını kullanır ve iki EMA yerine iki düz HO'yu karşılaştırır, bu yüzden her pencerenin kendi kenarının ötesinde bir hafızası yoktur.

## Formül

```text
OrtaFiyat = (Yüksek + Düşük) / 2; AO = HO(OrtaFiyat, 5) - HO(OrtaFiyat, 34)
```

## Parametreler

**Gerekli girdiler:** `high`, `low`

| Parametre | Varsayılan |
| --- | --- |
| `fast` | `5` |
| `slow` | `34` |

## Döndürdükleri

| Kolon |
| --- |
| `AO_5_34` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.awesome_oscillator(df['high'], df['low']).tail(3)
```

```text
date
2024-10-25   -1.058354
2024-10-26   -0.963254
2024-10-27   -0.985917
Name: AO_5_34, dtype: float64
```

**Accessor biçimi:** `df.zta.awesome_oscillator(...)`

## Nasıl okunur

Histogramı `macd`'nin histogramı gibi okuyun: pozitif ve yükselen değerler güçlenen yukarı yönlü momentumu gösterir; sıfır çizgisinde bir renk/işaret değişimi hangi tarafın (5-bar mı 34-bar mı) şu an baskın olduğundaki bir kaymayı işaret eder. Sıkça anılan bir formasyon ("çanak"), sıfırın aynı tarafında art arda iki ya da üç barın kısalıp sonra birinin uzamasını arar.

## Dikkat edilmesi gerekenler

Kapanış yerine barın orta noktasını kullanması, AO'nun düz kapanan bir barda bile sadece gün içi bir fitilden dolayı hareket edebileceği anlamına gelir — yönü değil, aralığı okur. Sınırsız ve fiyat biriminde ifade edildiği için, 0-100 aralığındaki bir osilatörün aksine semboller ya da fiyat seviyeleri arasında karşılaştırılamaz.

## Kaynak

Formül kaynağı: [https://www.metatrader5.com/en/terminal/help/indicators/bw_indicators/awesome](https://www.metatrader5.com/en/terminal/help/indicators/bw_indicators/awesome)
