# Çok Ölçekli Dalgacık Varyansı (MODWT)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/wavelet_variance.md)

`zeonta.wavelet_variance()` — Multi-scale volatility (MODWT): how much movement lives at each timescale.

## Ne ölçer

atr() ve yuvarlanan standart sapmanın ikisi de 'fiyat ne kadar hareket etti' sorusuna tek, karıştırılmış bir sayıyla cevap verir. Percival & Walden'ın 'Wavelet Methods for Time Series Analysis' (2000) kitabı — bu tekniğin standart referans kaynağı — bu sayıyı Maksimal Örtüşmeli DWT (MODWT) kullanarak zaman ölçeğine göre ayırır: enerji-koruyucu olduğu için (sıradan bir DWT'den farklı olarak), ortaya çıkan ölçek-başı varyanslar toplam varyansın gerçek bir ayrışımıdır, bağımsız veya örtüşen okumalar değildir. Bu kütüphanedeki `wavelet_denoise`, filtrelenmiş bir fiyat yeniden inşa etmek için sıradan bir DWT kullanır; bu ise oynaklığın şeklini tanımlamak için ham ölçek-başı enerjiyi korur.

## Formül

```text
Her yuvarlanan pencere için: MODWT ile (norm=True, trim_approx=True) `level` sayıda detay bandına ayrıştır; her j seviyesi için WVAR_j = ortalama(detay_bandı_j ** 2), 1 (en ince) ile `level` (en kaba) arasında
```

## Parametreler

**Gerekli girdiler:** `close`

| Parametre | Varsayılan |
| --- | --- |
| `window` | `64` |
| `wavelet` | `'db4'` |
| `level` | `5` |

## Döndürdükleri

| Kolon |
| --- |
| `WVAR_1` |
| `WVAR_2` |
| `WVAR_3` |
| `WVAR_4` |
| `WVAR_5` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.wavelet_variance(df['close']).tail(3)
```

```text
              WVAR_1    WVAR_2    WVAR_3    WVAR_4    WVAR_5
date                                                        
2024-10-25  0.057980  0.051089  0.129020  0.131990  0.287943
2024-10-26  0.057469  0.066789  0.128876  0.181626  0.311155
2024-10-27  0.061135  0.104635  0.155178  0.230250  0.334630
```

**Accessor biçimi:** `df.zta.wavelet_variance(...)`

## Nasıl okunur

Her `WVAR_j` kolonu, ikişer katlanan bir bar bandını kapsar (`WVAR_1` ~ 2-4 bar, `WVAR_2` ~ 4-8 bar, ve `WVAR_{level}`'e kadar böyle devam eder). En ince bantların baskın olduğu bir bar çoğunlukla yüksek frekanslı gürültüdür (ince emir defterleri, HFT çalkantısı); en kaba bantların baskın olduğu bir bar ise gerçek, daha yavaş bir hareketi yansıtır — tek bir ATR okumasının yapamayacağı bir ayrım, çünkü o her zaman tüm zaman ölçeklerini tek bir sayıda karıştırır. Yatırımcılar bunu bir rejim okuması olarak kullanır: şu anda fiyat hareketini hangi tür oynaklığın sürüklediği.

## Dikkat edilmesi gerekenler

Bu, Percival & Walden'ın *yansız* tahmin edicisi (sınır etkisindeki katsayıları dışlayan) yerine *yanlı* dalgacık-varyans tahmin edicisini kullanır (penceredeki her katsayının ortalaması) — daha basittir ve her window/level çifti için her zaman tanımlıdır, bedeli ise akademik literatürün belgelediği küçük bir yanlılıktır. `window`, `2**level`'in tam katı olmak zorundadır — bu, ayarlanabilir bir varsayılan değil, sert bir MODWT gereksinimidir. Ve `wavelet_denoise` gibi, her bar tüm seri üzerinde tek bir geçiş yerine kendi ayrıştırmasını yeniden çalıştırır — büyük bir geçmiş üzerinde kullanmadan önce kendi verinizde ölçün (bkz. `BENCHMARKS.md`).

## Kaynak

Formül kaynağı: [https://staff.washington.edu/dbp/wmtsa.html](https://staff.washington.edu/dbp/wmtsa.html)
