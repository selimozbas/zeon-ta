# Sıfır Gecikmeli Üssel Hareketli Ortalama (ZLEMA)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/zlema.md)

`zeonta.zlema()` — An EMA fed de-lagged data, to track price with less delay than a plain EMA.

## Ne ölçer

Ehlers & Way'in [ema](ema.md)'nın kendi içindeki gecikmeye cevabı: düzleştirme formülünün kendisini değiştirmek yerine, *içine giren* şeyi değiştirirler — EMA'ya ham kapanış yerine fiyatın gecikmesi giderilmiş bir sürümünü (bugünün kapanışı artı `lag` bar önceden ne kadar hareket ettiği) besler.

## Formül

```text
lag = taban((n-1)/2); veri[t] = Kapanış[t] + (Kapanış[t] - Kapanış[t-lag]); ZLEMA = EMA(veri, n)
```

## Parametreler

**Gerekli girdiler:** `close`

| Parametre | Varsayılan |
| --- | --- |
| `length` | `20` |

## Döndürdükleri

| Kolon |
| --- |
| `ZLEMA_20` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.zlema(df['close']).tail(3)
```

```text
date
2024-10-25    90.105026
2024-10-26    89.808691
2024-10-27    89.394787
Name: ZLEMA_20, dtype: float64
```

**Accessor biçimi:** `df.zta.zlema(...)`

## Nasıl okunur

EMA ailesinden herhangi bir çizgi gibi okunur — aynı uzunluktaki `ema`'ya daha hızlı tepki veren bir alternatif, bedeli ise keskin bir dönüşte daha fazla aşırı tepki vermesidir (gecikmeyi kaldırmak çizgiyi her iki yönde de hareket etmeye daha istekli yapar).

## Dikkat edilmesi gerekenler

Gecikme-iptali yalnızca düz bir çizgide tamdır; gerçek fiyat düz bir çizgi değildir, bu yüzden bir miktar gecikme kalır ve isimdeki 'sıfır' harfiyen değil, hedeflenen bir şeydir.

## Kaynak

Formül kaynağı: [https://user42.tuxfamily.org/chart/manual/Zero_002dLag-Exponential-Moving-Average.html](https://user42.tuxfamily.org/chart/manual/Zero_002dLag-Exponential-Moving-Average.html)
