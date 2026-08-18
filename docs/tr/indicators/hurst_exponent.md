# Hurst Üsteli (Yeniden Ölçeklenmiş Aralık Analizi)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/hurst_exponent.md)

`zeonta.hurst_exponent()` — How persistent recent price moves are: trending, mean-reverting, or a random walk.

## Ne ölçer

Harold Hurst bunu 1950'lerde, piyasalara uygulanmasından çok önce, Nil Nehri'nin çok yıllık taşkın kayıtlarını incelerken geliştirdi; Yeniden Ölçeklenmiş Aralık (R/S) analizi bunun için klasik tahmin edicidir. Bir getiri serisine uygulandığında *kalıcılığı* ölçer — bir hareketin aynısının devamıyla mı (trend) yoksa bir dönüşle mi (ortalamaya dönüş) takip edilme eğiliminde olduğunu — bu, kütüphanedeki diğer tüm indikatörlerin sorduğundan temelden farklı bir sorudur; onların hepsi seriyi üreten istatistiksel karakteri değil, doğrudan fiyat/momentumu ölçer.

## Formül

```text
Her bir gecikme n için: pencerenin logaritmik getirilerini n boyutunda parçalara bölün; R/S(n) = parçalar üzerinden ortalama(kümülatif ortalama-düzeltilmiş sapmanın aralığı) / parçanın standart sapması; H = log(R/S)'nin log(n)'e karşı regresyonunun eğimi
```

## Parametreler

**Gerekli girdiler:** `close`

| Parametre | Varsayılan |
| --- | --- |
| `window` | `100` |

## Döndürdükleri

| Kolon |
| --- |
| `HURST_100` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.hurst_exponent(df['close']).tail(3)
```

```text
date
2024-10-25    0.641674
2024-10-26    0.603123
2024-10-27    0.584958
Name: HURST_100, dtype: float64
```

**Accessor biçimi:** `df.zta.hurst_exponent(...)`

## Nasıl okunur

``H ≈ 0,5``: hafızasız bir rastgele yürüyüş — geçmiş hareketler gelecek hakkında hiçbir şey söylemez. ``H > 0,5``: trend/kalıcı — bir hareketin aynısının devamıyla takip edilme eğilimi. ``H < 0,5``: ortalamaya dönüş/kalıcı-olmayan — bir hareketin bir dönüşle takip edilme eğilimi. Birçok yatırımcı bunu bir *rejim filtresi* olarak kullanır: ``H`` rahatça 0,5'in üzerindeyken trend takip eden araçlara, altındayken osilatör/ortalamaya-dönüş araçlarına yaslanır.

## Dikkat edilmesi gerekenler

R/S analizi klasik (1951) tahmin edicidir, tek yöntem değildir — başka yöntemler de (DFA, genelleştirilmiş Hurst üsteli) vardır ve her zaman R/S ile aynı veride hemfikir olmazlar; bu yüzden bunu serinin sabit bir fiziksel sabiti değil, belirli, standart bir yöntemden gelen bir tahmin olarak ele alın. Ayrıca, açık farkla, bu kütüphanedeki en yavaş indikatördür (kendi docstring'ine ve `BENCHMARKS.md`'ye bakın) — burada diğer her indikatörün kullandığı tek geçişli vektörleştirme yerine, her barda birden fazla gecikme değeri üzerinden yuvarlanan bir regresyon.

## Kaynak

Formül kaynağı: [https://en.wikipedia.org/wiki/Hurst_exponent](https://en.wikipedia.org/wiki/Hurst_exponent)
