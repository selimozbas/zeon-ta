# Formüller nasıl doğrulanır

[English](../en/methodology.md)

`zeon-ta`'daki her indikatör, bağımsız ve güvenilir bir kaynağa karşı
kontrol edilmiş bir formülden uygulanır — hiçbir zaman tek bir kaynağa körü
körüne güvenilerek, hiçbir zaman ezberden değil. Bu sayfa nedenini ve sürecin
gerçekte nasıl işlediğini anlatır.

## Bu neden katı bir kural

Bu projenin erken döneminde, iki indikatör tek bir kaynağın belirttiği
formülden uygulandı ve ikisi de ikinci bir kaynakla karşılaştırıldığında
yanlış çıktı:

- **`trend_channel`**'ın bantları, fiyatın *pencere ortalaması* etrafındaki
  saçılımını ölçüyordu; oysa standart tanım (ve kaynağın kendi metni dikkatle
  okunduğunda) *uydurulan regresyon çizgisi* etrafındaki saçılımı istiyordu —
  kanalı yanlış bir şekilde şişiren, farklı ve daha küçük bir sayı.
- **`squeeze`**'in momentum orta çizgisi, üç girdisinin düz bir üçlü
  ortalamasını kullanıyordu; oysa kanonik TTM Squeeze formülü, önce ikisini
  birlikte ağırlıklandıran özel bir iç içe ortalama kullanır.

Bu hatalardan hiçbiri bir yazım hatası değildi — ikisi de bir kaynağın
ifadesine, indikatörün başka yerlerde gerçekte nasıl hesaplandığını kontrol
etmeden güvenmekten kaynaklandı. Aşağıdaki doğrulama kuralının var olmasının
tek nedeni budur ve bu kural, yalnızca hata veren indikatörlere değil, o
zamandan beri eklenen her indikatöre uygulanır.

## Süreç

1. **Formülü birincil, güvenilir bir kaynakta bulun.**
   [StockCharts ChartSchool](https://chartschool.stockcharts.com/) tercih
   edilir — bakımı yapılıyor, varsa orijinal geliştiriciye atıf yapıyor ve
   varsayılanlar ile uç durumlar konusunda kesin. ChartSchool'da bir
   indikatör için sayfa yoksa, geri düşüş sırası: Fidelity'nin Teknik
   İndikatör Kılavuzu, Wikipedia, ya da belirli bir platforma özgü
   indikatörler için o platformun kendi resmi dokümantasyonu (MetaTrader5,
   TradingView).
2. **İlk kaynak bir varsayılan parametre, bir yuvarlama kuralı, ilk barın**
   nasıl ele alındığı ya da sıfıra bölme uç durumu konusunda belirsizse
   ikinci bir kaynakla karşılaştırın. İki kaynağın temel formülde
   anlaşıp bir varsayılanda ayrışması yaygındır ve docstring'de belirtilmeye
   değer; iki kaynağın formülün kendisinde etkin biçimde anlaşmazlığa
   düşmesi ise rastgele birini seçmek yerine aramaya devam etme işaretidir.
3. **Kaynağı kaydedin.** Doğrulanan URL, fonksiyonun
   `@indicator(reference=...)` alanına ve docstring'inin `References`
   bölümüne yazılır; böylece kodu okuyan herkes — yalnızca bu sayfayı okuyan
   değil — uygulamayı aynı kaynağa karşı kontrol edebilir.
4. **Her örneği hesaplayın, asla tahmin etmeyin.** Bir docstring'in
   `Examples` bloğu test paketi tarafından çalıştırılır, ama *docstring'e
   yazılan değeri* önce bir insan yazar. Bu kütüphanenin geçmişindeki
   birkaç örnek başlangıçta tahmin edildi ve gerçekten hesaplandığında
   yanlış çıktı — `hma`'nın doctest'i düz bir rampada `30.0` olarak tahmin
   edildi, gerçekte `29.3333` idi; `williams_r`'ınki `0.0` olarak tahmin
   edildi, gerçekte `-0.0` idi (gerçek bir float işareti uç durumu);
   `stoch_rsi`'ınki `100.0` olarak tahmin edildi, gerçekte `50.0` idi (RSI'nin
   kendi tavanına sabitlenmesinin tetiklediği yatay-piyasa kuralı). Bunların
   hiçbiri formül üzerine daha çok düşünülerek yakalanmadı; hepsi kodu
   güvenmeden önce çalıştırarak yakalandı.
5. **Yukarıdaki iki hatayı yakalayacak testler yazın.** Uygulamanın kendi
   çıktısına karşı değil, doğrulanmış formüle karşı elle izlenmiş en az bir
   altın değer — bir hatayı yakalamak yerine yeniden üreten bir test,
   test olmamasından daha kötüdür.

## Bunun kapsamadığı

Bir avuç indikatör (registry'de `reference` yerine `lesson` ile
işaretlenmiş), bu projenin fonksiyon başına dış kaynak atıfına geçmesinden
öncesine ait; aynı standart, yaygın olarak yayımlanmış tanımları izlerler,
sadece docstring'lerinde ayrıca atıfta bulunulan bir URL olmadan. O zamandan
beri eklenen her indikatör — bkz. `CHANGELOG.md`'nin `0.2.0` girdisinden
itibaren — açık bir `reference` taşır.

Yeni bir indikatör eklerken bunun nasıl uygulandığı için bkz.
[CONTRIBUTING.md](../../CONTRIBUTING.md#formula-verification-is-not-optional).
