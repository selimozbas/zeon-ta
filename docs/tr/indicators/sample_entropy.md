# Örnek Entropi (SampEn)

[← Tüm indikatörler](../index.md) · [English](../../en/indicators/sample_entropy.md)

`zeonta.sample_entropy()` — Sample Entropy: how unpredictable a series is, from 0 (regular) upward (irregular).

## Ne ölçer

Richman ve Moorman (2000), daha önceki Yaklaşık Entropi'deki (ApEn, Pincus 1991) belirli bir kusuru düzeltmek için Örnek Entropi'yi geliştirdi: ApEn bir şablonu kendisiyle eşleşiyor sayar, bu da onu — daha kısa serilerde daha fazla olmak üzere — verinin gerçekte olduğundan daha düzenli okumaya yanlı hale getirir. SampEn öz-eşleşmeleri tamamen dışlar. hurst_exponent/dfa'dan farklı bir soru sorar: bir serinin trend mi yoksa ortalamaya mı döndüğünü değil, kısa vadeli kendi kalıplarını ne kadar tekrarladığını, bu kalıpların hangi yöne işaret ettiğinden bağımsız olarak.

## Formül

```text
Log-getiri penceresinden her uzunluk-m ve uzunluk-(m+1) şablonu oluştur; B = tolerans r*std(pencere) içindeki uzunluk-m şablon çiftlerinin sayısı (öz-eşleşmeler hariç); A = uzunluk m+1'de aynı sayım; SampEn = -ln(A/B)
```

## Parametreler

**Gerekli girdiler:** `close`

| Parametre | Varsayılan |
| --- | --- |
| `window` | `100` |
| `m` | `2` |
| `r` | `0.2` |

## Döndürdükleri

| Kolon |
| --- |
| `SAMPEN_100_2_0.2` |

## Kullanım

Örnekler, `df` olarak yüklenen `tests/data/ohlcv.csv` içindeki 300 barlık OHLCV fixture üzerinde çalışır. Gösterilen çıktı gerçek çıktıdır.

```python
import pandas as pd
import zeonta

df = pd.read_csv('tests/data/ohlcv.csv', parse_dates=['date']).set_index('date')
```

```python
zeonta.sample_entropy(df['close']).tail(3)
```

```text
date
2024-10-25    2.433613
2024-10-26    2.451005
2024-10-27    2.433613
Name: SAMPEN_100_2_0.2, dtype: float64
```

**Accessor biçimi:** `df.zta.sample_entropy(...)`

## Nasıl okunur

Düşük değerler (0'a yakın), pencerenin kısa kalıpları tekrarlamaya devam ettiği anlamına gelir — düzenli, daha öngörülebilir davranış. Yüksek değerler, tekrarlayan yapının az ya da hiç olmadığı anlamına gelir — düzensiz, gürültüye daha yakın. hurst_exponent/dfa'nın aksine, buradaki yüksek bir okuma fiyatın *hangi yöne* hareket etmesinin muhtemel olduğunu söylemez, yalnızca son davranışının kısa tekrarlayan bir kalıpla karakterize edilmesinin daha zor olduğunu söyler.

## Dikkat edilmesi gerekenler

Bu kütüphanedeki açık farkla en yavaş indikatör — her bar kendi penceresindeki her şablon çiftini karşılaştırır (O(pencere^2)), buradaki çoğu indikatörün kullandığı tek vektörleştirilmiş geçiş değil, hatta hurst_exponent/dfa'nın kendi bar-başı döngülerinden de yavaş (bkz. `BENCHMARKS.md`). `m` ve `r` göz ardı edilecek varsayılanlar değil, gerçek seçimlerdir: Richman & Moorman'ın kendi örnekleri `m=2` ve pencerenin standart sapmasının `0,1` ile `0,25`'i arasında bir `r` kullanır, farklı bir eşleştirme sonucu değiştirir — bu, literatürde kullanılan tek parametreleme değil, belirli, standart bir parametrelemedir.

## Kaynak

Formül kaynağı: [https://physionet.org/content/sampen/1.0.0/](https://physionet.org/content/sampen/1.0.0/)
