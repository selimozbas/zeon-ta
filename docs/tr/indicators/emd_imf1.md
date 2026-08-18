# Ampirik Mod Ayrıştırması — Birinci IMF

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/emd_imf1.md)

`zeonta.emd_imf1()` — Empirical Mode Decomposition's first IMF: the dominant local oscillation.

## Ne ölçer

Huang ve ark. (1998), durağan olmayan ve doğrusal olmayan sinyaller için — bir fiyat serisi de dahil — Fourier ve dalgacık analizine alternatif olarak EMD'yi geliştirdi. Sabit bir taban üzerine izdüşüm almak yerine (sinüsler, ya da bir dalgacığın sabit ana fonksiyonu), EMD kendi taban fonksiyonlarını doğrudan verinin yerel ekstremumlarından türetir. Bu kütüphane, tam bir ayrıştırmanın üreteceği şeyin yalnızca ilkini sunar: en hızlı yerel salınım; daha yavaş bileşenler (sonraki IMF'ler ve tam bir ayrıştırmanın bittiği artık trend) dışarıda bırakılır, çünkü tam bir ayrıştırmanın IMF sayısı veriye göre değişir ve sabit-kolon çıktıya uymaz.

## Formül

```text
Yuvarlanan bir pencere içinde close'u salla (sift): yerel maksimum ve minimumlarından doğal kübik spline'lar geçirerek üst/alt zarfları oluştur, ortalamalarını çıkar, SD < sd_threshold ya da max_iterations'a ulaşılana kadar sonuç üzerinde tekrarla; sonuç birinci Intrinsic Mode Function'dır
```

## Parametreler

**Gerekli girdiler:** `close`

| Parametre | Varsayılan |
| --- | --- |
| `window` | `100` |
| `max_iterations` | `50` |
| `sd_threshold` | `0.25` |

## Döndürdükleri

| Kolon |
| --- |
| `EMDIMF1_100` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.emd_imf1(df['close']).tail(3)
```

```text
date
2024-10-25    0.765580
2024-10-26   -0.421528
2024-10-27   -1.444587
Name: EMDIMF1_100, dtype: float64
```

**Accessor biçimi:** `df.zta.emd_imf1(...)`

## Nasıl okunur

`close - zeonta.emd_imf1(close, window)`, tam bir ayrıştırmanın izole edeceği trend/döngü artığına yaklaşır, ama tam olarak o artık değildir — yalnızca bir IMF çıkarılmıştır, monoton bir trende kadar inen tam yinelemeli ayrıştırma değil. Doğrudan kullanıldığında, IMF1 bir döngü/gürültü çıkarımı gibi davranır — `wavelet_denoise`'in çıkardığına benzer bir ruhta ama ters yönden: bu, hızlı bileşeni filtrelemek yerine onu tutar.

## Dikkat edilmesi gerekenler

Bu kütüphanedeki açık farkla en pahalı indikatör: her bar kendi penceresi üzerinde yinelemeli bir spline-uydurma döngüsünü yeniden çalıştırır, tek bir vektörleştirilmiş geçiş değil (bkz. `BENCHMARKS.md`). Sınır işleme, genel olarak EMD'nin bilinen, gerçek bir zayıf noktasıdır — bu uygulama, zarf spline'larını pencerenin kendi ilk/son örneğine kasıtlı olarak sabitlemez (önceki bir sürüm sabitliyordu ve bunun sınırdaki her salınmış değeri tam olarak 0,0'a zorladığı ortaya çıktı — formüle güvenmek yerine şüpheli derecede tam bir sıfırın fark edilmesiyle yakalandı); doğal kübik spline'ın en dıştaki gerçek ekstremumun ötesine ekstrapolasyon yapmasına izin vermek bu belirli sorunu önler, ama sınır barları bu yüzden yine de herhangi bir EMD penceresinin en güvenilmez kısmıdır.

## Kaynak

Formül kaynağı: [https://doi.org/10.1098/rspa.1998.0193](https://doi.org/10.1098/rspa.1998.0193)
