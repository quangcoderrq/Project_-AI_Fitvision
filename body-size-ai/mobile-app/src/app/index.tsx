import React, { useState } from 'react';
import {
  StyleSheet,
  View,
  Text,
  Image,
  ScrollView,
  TouchableOpacity,
  Modal,
  SafeAreaView,
  TextInput,
  Alert,
  Dimensions,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import Constants from 'expo-constants';
import BodySizeWidget from '../components/BodySizeWidget';

const { width } = Dimensions.get('window');

// Detect local development IP from Expo packager
const getInitialApiUrl = () => {
  const hostUri = Constants.expoConfig?.hostUri || Constants.manifest2?.extra?.expoGoLaunchMetadata?.manifest?.hostUri;
  if (hostUri) {
    const ip = hostUri.split(':')[0];
    if (ip && ip !== 'localhost' && ip !== '127.0.0.1') {
      return `http://${ip}:8000`;
    }
  }
  return 'http://127.0.0.1:8000';
};

export default function ProductScreen() {
  const [modalVisible, setModalVisible] = useState(false);
  const [selectedSize, setSelectedSize] = useState<string | null>(null);
  
  // AI Prediction Results State
  const [aiSize, setAiSize] = useState<string | null>(null);
  const [aiShirtSize, setAiShirtSize] = useState<string | null>(null);
  const [aiPantsSize, setAiPantsSize] = useState<string | null>(null);

  // Connection settings
  // Automatically detects local development IP when running in Expo
  const [apiUrl, setApiUrl] = useState(getInitialApiUrl());
  const [showConfig, setShowConfig] = useState(false);

  const product = {
    name: 'Minimalist Linen Tailored Blazer',
    price: '$189.00',
    originalPrice: '$245.00',
    rating: '4.9',
    reviews: '124 đánh giá',
    description: 'Áo blazer phom suông tối giản được may từ chất liệu linen tự nhiên kết hợp cotton cao cấp, thoáng mát, đứng phom và mang lại cảm giác thoải mái tối đa cho cả ngày làm việc hay dạo phố.',
    sizes: ['XS', 'S', 'M', 'L', 'XL', 'XXL'],
  };

  const handleSizeSelect = (size: string) => {
    setSelectedSize(size);
  };

  const handleSizePredicted = (recommendedSize: string, shirtSize: string, pantsSize: string) => {
    setAiSize(recommendedSize);
    setAiShirtSize(shirtSize);
    setAiPantsSize(pantsSize);
    
    // Automatically apply size to cart selection
    if (recommendedSize && recommendedSize !== 'N/A') {
      setSelectedSize(recommendedSize);
      Alert.alert(
        '✨ Đã áp dụng Size AI!',
        `Hệ thống AI đề xuất Size [${recommendedSize}] phù hợp nhất với số đo cơ thể bạn.`,
        [{ text: 'Tuyệt vời' }]
      );
    }
  };

  const handleAddToCart = () => {
    if (!selectedSize) {
      Alert.alert('Chọn kích cỡ', 'Vui lòng chọn size áo trước khi thêm vào giỏ hàng.');
      return;
    }
    Alert.alert(
      '🛒 Đã thêm vào giỏ hàng',
      `Thêm sản phẩm "${product.name}" - Size [${selectedSize}] thành công!`,
      [{ text: 'Tiếp tục mua sắm' }]
    );
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView style={styles.container} contentContainerStyle={{ paddingBottom: 60 }}>
        {/* Top Navbar */}
        <View style={styles.topNavbar}>
          <TouchableOpacity style={styles.navBtn}>
            <Ionicons name="chevron-back" size={24} color="#0f172a" />
          </TouchableOpacity>
          <Text style={styles.navTitle}>Chi tiết sản phẩm</Text>
          <View style={{ flexDirection: 'row', gap: 12 }}>
            <TouchableOpacity style={styles.navBtn} onPress={() => setShowConfig(!showConfig)}>
              <Ionicons 
                name={showConfig ? "settings" : "settings-outline"} 
                size={22} 
                color={showConfig ? "#6366f1" : "#0f172a"} 
              />
            </TouchableOpacity>
            <TouchableOpacity style={styles.navBtn}>
              <Ionicons name="cart-outline" size={24} color="#0f172a" />
              {selectedSize && <View style={styles.cartBadge} />}
            </TouchableOpacity>
          </View>
        </View>

        {/* Server Config Drawer */}
        {showConfig && (
          <View style={styles.configDrawer}>
            <View style={{ flexDirection: 'row', alignItems: 'center', marginBottom: 8 }}>
              <Ionicons name="server" size={16} color="#6366f1" style={{ marginRight: 6 }} />
              <Text style={styles.configTitle}>Kết nối Máy chủ AI</Text>
            </View>
            
            <TextInput
              style={styles.configInput}
              value={apiUrl}
              onChangeText={setApiUrl}
              placeholder="http://192.168.x.x:8000"
              autoCapitalize="none"
              autoCorrect={false}
            />

            <View style={styles.configGuide}>
              <Text style={styles.guideText}>
                ⚠️ <Text style={{ fontWeight: 'bold' }}>LƯU Ý KHI DÙNG THIẾT BỊ THẬT (EXPO GO):</Text>
              </Text>
              <Text style={[styles.guideText, { marginTop: 4 }]}>
                1. Hãy chắc chắn điện thoại và máy tính cùng kết nối chung một mạng Wi-Fi.
              </Text>
              <Text style={styles.guideText}>
                2. Điền URL là IP máy tính của bạn kèm cổng 8000 (Ví dụ: <Text style={{ fontWeight: 'bold', color: '#6366f1' }}>http://192.168.1.15:8000</Text>). Không dùng 'localhost' hay '127.0.0.1'.
              </Text>
              <Text style={styles.guideText}>
                3. Gõ <Text style={{ fontFamily: 'monospace', color: '#e11d48' }}>ipconfig</Text> trên cmd máy tính để tìm địa chỉ IPv4.
              </Text>
              <Text style={[styles.guideText, { color: '#16a34a', fontWeight: 'bold', marginTop: 6 }]}>
                🔌 Đã tự động phát hiện IP từ Expo: {getInitialApiUrl()}
              </Text>
            </View>
          </View>
        )}

        {/* Product Image */}
        <View style={styles.imageContainer}>
          <Image 
            source={require('@/assets/images/blazer.png')} 
            style={styles.productImage} 
            resizeMode="cover" 
          />
        </View>

        {/* Product Info */}
        <View style={styles.infoSection}>
          <View style={styles.priceRow}>
            <View style={{ flexDirection: 'row', alignItems: 'baseline', gap: 8 }}>
              <Text style={styles.priceText}>{product.price}</Text>
              <Text style={styles.originalPriceText}>{product.originalPrice}</Text>
            </View>
            <View style={styles.ratingBox}>
              <Ionicons name="star" size={14} color="#fbbf24" style={{ marginRight: 4 }} />
              <Text style={styles.ratingText}>{product.rating}</Text>
              <Text style={styles.reviewsText}>({product.reviews})</Text>
            </View>
          </View>

          <Text style={styles.productName}>{product.name}</Text>
          <Text style={styles.descriptionText}>{product.description}</Text>

          <View style={styles.divider} />

          {/* Size Selector Section */}
          <View style={styles.sizeSection}>
            <View style={styles.sizeHeader}>
              <Text style={styles.sectionTitle}>Chọn kích cỡ</Text>
              
              {/* Premium AI Button */}
              <TouchableOpacity 
                style={styles.aiButton}
                onPress={() => setModalVisible(true)}
              >
                <Ionicons name="sparkles" size={16} color="#fff" style={{ marginRight: 6 }} />
                <Text style={styles.aiButtonText}>Chọn Size bằng AI</Text>
              </TouchableOpacity>
            </View>

            {/* AI Recommendation Alert Banner (if calculated) */}
            {aiSize && (
              <View style={styles.aiAlertBanner}>
                <Ionicons name="sparkles" size={18} color="#6366f1" style={{ marginRight: 8 }} />
                <View style={{ flex: 1 }}>
                  <Text style={styles.aiAlertTitle}>🤖 Đề xuất bởi AI của bạn</Text>
                  <Text style={styles.aiAlertDesc}>
                    Cơ thể bạn vừa vặn nhất với size <Text style={{ fontWeight: 'bold', color: '#4f46e5' }}>{aiSize}</Text>.
                    {aiShirtSize && aiShirtSize !== 'N/A' && ` (Áo: ${aiShirtSize}`}
                    {aiPantsSize && aiPantsSize !== 'N/A' && `, Quần: ${aiPantsSize})`}
                  </Text>
                </View>
              </View>
            )}

            {/* Size Options Grid */}
            <View style={styles.sizeGrid}>
              {product.sizes.map((size) => {
                const isSelected = selectedSize === size;
                const isRecommended = aiSize === size;
                
                return (
                  <TouchableOpacity
                    key={size}
                    style={[
                      styles.sizeBox,
                      isSelected && styles.sizeBoxSelected,
                      isRecommended && styles.sizeBoxRecommended
                    ]}
                    onPress={() => handleSizeSelect(size)}
                  >
                    <Text style={[
                      styles.sizeText,
                      isSelected && styles.sizeTextSelected,
                      isRecommended && styles.sizeTextRecommended
                    ]}>
                      {size}
                    </Text>
                    {isRecommended && (
                      <View style={styles.recommendedDot} />
                    )}
                  </TouchableOpacity>
                );
              })}
            </View>

            {/* If user selects a size different from AI recommended size */}
            {aiSize && selectedSize && selectedSize !== aiSize && (
              <Text style={styles.aiMismatchHint}>
                💡 Kích thước bạn chọn khác với đề xuất của AI ({aiSize}). Hãy chọn lại {aiSize} để có trải nghiệm vừa vặn tốt nhất.
              </Text>
            )}
          </View>

          {/* Add to Cart Footer Actions */}
          <View style={styles.footerActions}>
            <TouchableOpacity style={styles.wishlistBtn}>
              <Ionicons name="heart-outline" size={24} color="#475569" />
            </TouchableOpacity>
            <TouchableOpacity style={styles.buyBtn} onPress={handleAddToCart}>
              <Ionicons name="cart" size={20} color="#fff" style={{ marginRight: 8 }} />
              <Text style={styles.buyBtnText}>Thêm vào giỏ hàng</Text>
            </TouchableOpacity>
          </View>
        </View>
      </ScrollView>

      {/* Embedded BodySizeWidget Modal */}
      <Modal
        animationType="slide"
        transparent={false}
        visible={modalVisible}
        onRequestClose={() => setModalVisible(false)}
      >
        <BodySizeWidget
          onClose={() => setModalVisible(false)}
          onSizePredicted={handleSizePredicted}
          apiUrl={apiUrl}
        />
      </Modal>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#fff',
  },
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  topNavbar: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f1f5f9',
    backgroundColor: '#fff',
  },
  navTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: '#0f172a',
  },
  navBtn: {
    padding: 6,
    position: 'relative',
  },
  cartBadge: {
    position: 'absolute',
    top: 4,
    right: 4,
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#6366f1',
  },
  configDrawer: {
    backgroundColor: '#f1f5f9',
    borderBottomWidth: 1,
    borderBottomColor: '#e2e8f0',
    padding: 16,
  },
  configTitle: {
    fontSize: 13,
    fontWeight: '700',
    color: '#1e293b',
  },
  configInput: {
    backgroundColor: '#fff',
    borderWidth: 1,
    borderColor: '#cbd5e1',
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 8,
    fontSize: 14,
    color: '#0f172a',
    marginTop: 6,
  },
  configGuide: {
    marginTop: 10,
    backgroundColor: '#fffbeb',
    borderRadius: 8,
    padding: 10,
    borderWidth: 1,
    borderColor: '#fef08a',
  },
  guideText: {
    fontSize: 11,
    color: '#713f12',
    lineHeight: 15,
  },
  imageContainer: {
    width: width,
    height: 380,
    backgroundColor: '#f1f5f9',
  },
  productImage: {
    width: '100%',
    height: '100%',
  },
  infoSection: {
    padding: 20,
    backgroundColor: '#fff',
    borderTopLeftRadius: 28,
    borderTopRightRadius: 28,
    marginTop: -20,
  },
  priceRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  priceText: {
    fontSize: 24,
    fontWeight: '800',
    color: '#e11d48',
  },
  originalPriceText: {
    fontSize: 16,
    color: '#94a3b8',
    textDecorationLine: 'line-through',
  },
  ratingBox: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#f8fafc',
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 20,
  },
  ratingText: {
    fontSize: 13,
    fontWeight: 'bold',
    color: '#1e293b',
  },
  reviewsText: {
    fontSize: 11,
    color: '#64748b',
    marginLeft: 4,
  },
  productName: {
    fontSize: 20,
    fontWeight: '800',
    color: '#0f172a',
    marginBottom: 10,
    lineHeight: 26,
  },
  descriptionText: {
    fontSize: 13,
    color: '#475569',
    lineHeight: 20,
  },
  divider: {
    height: 1,
    backgroundColor: '#f1f5f9',
    marginVertical: 20,
  },
  sizeSection: {
    marginBottom: 24,
  },
  sizeHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 14,
  },
  sectionTitle: {
    fontSize: 15,
    fontWeight: '700',
    color: '#1e293b',
  },
  aiButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#6366f1',
    borderRadius: 20,
    paddingHorizontal: 14,
    paddingVertical: 8,
    shadowColor: '#6366f1',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 3,
  },
  aiButtonText: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#fff',
  },
  aiAlertBanner: {
    flexDirection: 'row',
    backgroundColor: '#e0e7ff',
    borderWidth: 1.5,
    borderColor: '#c7d2fe',
    borderRadius: 12,
    padding: 14,
    marginBottom: 16,
    alignItems: 'center',
  },
  aiAlertTitle: {
    fontSize: 12,
    fontWeight: 'bold',
    color: '#4f46e5',
    marginBottom: 2,
  },
  aiAlertDesc: {
    fontSize: 11,
    color: '#4338ca',
    lineHeight: 16,
  },
  sizeGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
  },
  sizeBox: {
    width: (width - 40 - 30) / 4, // 4 columns
    height: 48,
    borderRadius: 10,
    borderWidth: 1.5,
    borderColor: '#e2e8f0',
    justifyContent: 'center',
    alignItems: 'center',
    position: 'relative',
    backgroundColor: '#fff',
  },
  sizeBoxSelected: {
    borderColor: '#0f172a',
    backgroundColor: '#0f172a',
  },
  sizeBoxRecommended: {
    borderColor: '#6366f1',
    borderWidth: 2,
    backgroundColor: '#f5f3ff',
  },
  sizeText: {
    fontSize: 14,
    fontWeight: '700',
    color: '#475569',
  },
  sizeTextSelected: {
    color: '#fff',
  },
  sizeTextRecommended: {
    color: '#4f46e5',
  },
  recommendedDot: {
    position: 'absolute',
    top: 4,
    right: 4,
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: '#6366f1',
  },
  aiMismatchHint: {
    fontSize: 11,
    color: '#e11d48',
    marginTop: 12,
    fontStyle: 'italic',
    lineHeight: 16,
  },
  footerActions: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 20,
    gap: 16,
  },
  wishlistBtn: {
    width: 50,
    height: 50,
    borderRadius: 12,
    borderWidth: 1.5,
    borderColor: '#cbd5e1',
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#fff',
  },
  buyBtn: {
    flex: 1,
    height: 50,
    backgroundColor: '#0f172a',
    borderRadius: 12,
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
  },
  buyBtnText: {
    color: '#fff',
    fontSize: 15,
    fontWeight: '700',
  },
});
