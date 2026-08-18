# Dalgacık ile Gürültüsü Giderilmiş Fiyat (Ayrık Dalgacık Dönüşümü)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/wavelet_denoise.md)

`zeonta.wavelet_denoise()` — Causal rolling wavelet (DWT) denoising: cuts noise without an EMA's lag.

## Ne ölçer

Dalgacık dönüşümleri, bir Fourier dönüşümü gibi seriyi frekans bantlarına ayırır, ama — Fourier'den farklı olarak — zaman lokalizasyonunu korur: bir frekansın yalnızca var olduğunu değil, *ne zaman* oluştuğunu da gösterir. Dalgacıkla gürültüsü giderilmiş teknik indikatörler üzerine akademik çalışmalar (örn. üzerine yeni indikatörler kurmadan önce getiri serisinin gürültüsünü gidermek) tam olarak bunu kullanarak gerçek fiyat yapısını, bir SMA/EMA'nın eklediği gecikme olmadan gürültüden ayırır. Klasik dalgacık gürültü giderme, tüm seriyi tek geçişte ayrıştırır; bu, çevrimdışı bir çalışma için sorun değildir ama her barın değerinin sonraki barlara bağlı olabileceği anlamına gelir. Bu uygulama bunun yerine, mevcut bardan sonrasını hiç kullanmadan, her yuvarlanan `window` için ayrıştırmayı sıfırdan yeniden çalıştırır — bunun canlı sinyal üretmesi gereken her şey için neden önemli olduğu için kendi docstring'ine bakın.

## Formül

```text
Her yuvarlanan pencere için: bir yaklaşım bandına ve `level` sayıda detay bandına DWT ile ayrıştır; sigma = MAD(en ince detay bandı) / 0,6745; her detay bandını sigma*sqrt(2*log(pencere)) eşiğinde yumuşak-eşikle; yeniden inşa et ve yalnızca pencerenin son örneğini tut
```

## Parametreler

**Gerekli girdiler:** `close`

| Parametre | Varsayılan |
| --- | --- |
| `window` | `64` |
| `wavelet` | `'db4'` |
| `level` | `2` |

## Döndürdükleri

| Kolon |
| --- |
| `WDENOISE_64_db4` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.wavelet_denoise(df['close']).tail(3)
```

```text
date
2024-10-25    90.191874
2024-10-26    89.518209
2024-10-27    88.777733
Name: WDENOISE_64_db4, dtype: float64
```

**Accessor biçimi:** `df.zta.wavelet_denoise(...)`

## Nasıl okunur

Bu bitmiş bir sinyal değil, bir yapı taşıdır: ham `close` yerine mevcut bir indikatöre beslenmek üzere gürültüsü giderilmiş bir fiyat serisi döndürür — örn. `zeonta.rsi(zeonta.wavelet_denoise(df['close']))` ya da `macd` için aynısı — böylece onun daha az gecikmeli bir sürümü elde edilir. Tek başına bir trend çizgisi olarak kullanıldığında, Super Smoother ya da Instantaneous Trendline'a yakın şekilde döner, ama gürültüyü sabit özyinelemeli bir filtre yerine frekans-bandı eşiklemesiyle reddeder.

## Dikkat edilmesi gerekenler

Yuvarlanan pencere, tek vektörleştirilmiş bir geçiş yerine her barın sıfırdan yeniden ayrıştırılması demektir — büyük bir geçmiş üzerinde kullanmadan önce kendi verinizde ölçün (bkz. `BENCHMARKS.md`). Dalgacık ailesi ve ayrıştırma seviyesi göz ardı edilecek varsayılanlar değil, gerçek seçimlerdir: `db4` ve seviye 2, dalgacıkla gürültüsü giderilmiş indikatörler üzerine yayımlanmış çalışmaların en sık kullandığı çifttir, ama farklı bir eşleştirme sonucu değiştirir. Ve daha uzun bir geriye bakış, daha yavaş tepki vermek pahasına daha düşük frekansları çözdüğü için, `window` de kütüphanedeki her düzleştiricinin yaptığı gecikme-gürültü ödünleşimini yapar — sadece farklı bir mekanizmayla.

## Kaynak

Formül kaynağı: [https://doi.org/10.1093/biomet/81.3.425](https://doi.org/10.1093/biomet/81.3.425)
