import React, { useState, useEffect } from 'react';
import {
  StyleSheet,
  View,
  Text,
  TouchableOpacity,
  TextInput,
  ScrollView,
  Image,
  ActivityIndicator,
  Alert,
  Dimensions,
  Platform,
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { Ionicons } from '@expo/vector-icons';
import { SafeAreaView } from 'react-native-safe-area-context';

const { width } = Dimensions.get('window');

// Default brands in case fetching fails
const DEFAULT_BRANDS = [
  { name: 'generic', available_regions: ['asia'], garment_types: ['both', 'shirt', 'pants'] },
  { name: 'zara', available_regions: ['eu', 'us', 'asia'], garment_types: ['both', 'shirt', 'pants'] },
  { name: 'hm', available_regions: ['eu', 'us', 'asia'], garment_types: ['both', 'shirt', 'pants'] },
  { name: 'uniqlo', available_regions: ['asia', 'us'], garment_types: ['both', 'shirt', 'pants'] },
];

interface BodySizeWidgetProps {
  onClose: () => void;
  onSizePredicted: (recommendedSize: string, shirtSize: string, pantsSize: string) => void;
  apiUrl: string;
}

export default function BodySizeWidget({ onClose, onSizePredicted, apiUrl }: BodySizeWidgetProps) {
  const [step, setStep] = useState(1);
  const [brands, setBrands] = useState<any[]>(DEFAULT_BRANDS);
  const [loadingBrands, setLoadingBrands] = useState(false);

  // Form State
  const [height, setHeight] = useState('170');
  const [weight, setWeight] = useState('65');
  const [gender, setGender] = useState<'male' | 'female'>('male');
  const [brand, setBrand] = useState('generic');
  const [region, setRegion] = useState('asia');
  const [garmentType, setGarmentType] = useState<'both' | 'shirt' | 'pants'>('both');
  const [ignoreBaggyWarning, setIgnoreBaggyWarning] = useState(false);

  // Media State
  const [imageUri, setImageUri] = useState<string | null>(null);

  // Response State
  const [prediction, setPrediction] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [loadingText, setLoadingText] = useState('Đang gửi dữ liệu...');
  const [error, setError] = useState<string | null>(null);

  // Dynamic loading messages
  useEffect(() => {
    if (!loading) return;
    const texts = [
      'Đang upload hình ảnh lên máy chủ...',
      'Hệ thống AI đang phân tích đường nét cơ thể...',
      'Đang trích xuất các điểm đo nhân trắc học...',
      'Đang khớp thông số với bảng size tiêu chuẩn...',
      'Hoàn tất phân tích cơ thể!',
    ];
    let idx = 0;
    const interval = setInterval(() => {
      if (idx < texts.length - 1) {
        idx++;
        setLoadingText(texts[idx]);
      }
    }, 2500);

    return () => clearInterval(interval);
  }, [loading]);

  // Fetch available brands on mount
  useEffect(() => {
    const fetchBrands = async () => {
      setLoadingBrands(true);
      try {
        const res = await fetch(`${apiUrl}/brands`);
        if (res.ok) {
          const data = await res.json();
          if (data && data.brands) {
            setBrands(data.brands);
          }
        }
      } catch (err) {
        console.log('Failed to fetch brands, using local cache:', err);
      } finally {
        setLoadingBrands(false);
      }
    };
    fetchBrands();
  }, [apiUrl]);

  // Auto-select region when brand changes
  useEffect(() => {
    const currentBrand = brands.find((b) => b.name === brand);
    if (currentBrand && currentBrand.available_regions?.length > 0) {
      if (!currentBrand.available_regions.includes(region)) {
        setRegion(currentBrand.available_regions[0]);
      }
    }
  }, [brand, brands]);

  // Image Selection and Camera
  const requestPermission = async (type: 'camera' | 'library') => {
    if (type === 'camera') {
      const { status } = await ImagePicker.requestCameraPermissionsAsync();
      return status === 'granted';
    } else {
      const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
      return status === 'granted';
    }
  };

  const handlePickImage = async () => {
    const hasPermission = await requestPermission('library');
    if (!hasPermission) {
      Alert.alert('Quyền truy cập', 'Vui lòng cấp quyền truy cập thư viện ảnh để tiếp tục.');
      return;
    }

    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ['images'],
      allowsEditing: true,
      quality: 0.8,
    });

    if (!result.canceled && result.assets?.[0]?.uri) {
      setImageUri(result.assets[0].uri);
      setStep(2); // Go to image confirmation & preview step
    }
  };

  const handleTakePhoto = async () => {
    const hasPermission = await requestPermission('camera');
    if (!hasPermission) {
      Alert.alert('Quyền truy cập', 'Vui lòng cấp quyền chụp ảnh để tiếp tục.');
      return;
    }

    const result = await ImagePicker.launchCameraAsync({
      allowsEditing: true,
      quality: 0.8,
    });

    if (!result.canceled && result.assets?.[0]?.uri) {
      setImageUri(result.assets[0].uri);
      setStep(2); // Go to image confirmation & preview step
    }
  };

  // Predict API call
  const handlePredict = async (forceIgnoreBaggy = false) => {
    if (!imageUri) {
      Alert.alert('Thiếu ảnh', 'Vui lòng cung cấp hình ảnh để tiếp tục.');
      return;
    }

    const hVal = parseFloat(height);
    const wVal = parseFloat(weight);

    if (isNaN(hVal) || hVal < 100 || hVal > 250) {
      Alert.alert('Lỗi nhập liệu', 'Chiều cao phải nằm trong khoảng từ 100cm đến 250cm.');
      return;
    }

    if (isNaN(wVal) || wVal < 30 || wVal > 300) {
      Alert.alert('Lỗi nhập liệu', 'Cân nặng phải nằm trong khoảng từ 30kg đến 300kg.');
      return;
    }

    setLoading(true);
    setStep(3); // Loading screen
    setError(null);

    try {
      const data = new FormData();
      
      // Determine file name and extension
      const filename = imageUri.split('/').pop() || 'photo.jpg';
      const match = /\.(\w+)$/.exec(filename);
      const type = match ? `image/${match[1]}` : `image/jpeg`;

      if (Platform.OS === 'web') {
        const fileRes = await fetch(imageUri);
        const blob = await fileRes.blob();
        data.append('image', blob, filename);
      } else {
        // React Native FormData format for files
        data.append('image', {
          uri: imageUri,
          name: filename,
          type,
        } as any);
      }

      data.append('height', hVal.toString());
      data.append('weight', wVal.toString());
      data.append('gender', gender);
      data.append('brand', brand);
      data.append('region', region);
      data.append('image_type', garmentType === 'both' ? 'full' : (garmentType === 'shirt' ? 'upper' : 'lower'));
      data.append('ignore_baggy_warning', (forceIgnoreBaggy || ignoreBaggyWarning) ? 'true' : 'false');

      const response = await fetch(`${apiUrl}/predict/upload`, {
        method: 'POST',
        body: data,
      });

      if (!response.ok) {
        throw new Error(`Server returned code ${response.status}`);
      }

      const result = await response.json();
      
      if (result.success) {
        setPrediction(result);
        setStep(4); // Results screen
      } else {
        // AI returned validation errors or buggy warnings
        if (result.baggy_clothes_detected && !forceIgnoreBaggy) {
          // Keep at loading state, let user decide or render warning inside widget
          setPrediction(result);
          setStep(5); // Custom Baggy Warning step
        } else {
          setError(result.error || 'Dự đoán thất bại từ máy chủ.');
          setStep(2); // Go back to preview
        }
      }
    } catch (err: any) {
      console.error(err);
      setError(`Không thể kết nối đến máy chủ AI: ${err.message || 'Lỗi mạng'}`);
      setStep(2); // Go back to preview
    } finally {
      setLoading(false);
    }
  };

  const handleApplySize = () => {
    if (!prediction) return;
    const recommendedSize = prediction.predicted_size || 'N/A';
    const shirtSize = prediction.shirt_size?.recommended_size || 'N/A';
    const pantsSize = prediction.pants_size?.recommended_size || 'N/A';
    
    onSizePredicted(recommendedSize, shirtSize, pantsSize);
    onClose();
  };

  // Guide texts
  const guides = {
    both: {
      title: 'Chụp ảnh toàn thân',
      tips: [
        'Đứng thẳng lưng, chụp từ đầu đến chân.',
        'Mặc quần áo vừa vặn (không quá rộng).',
        'Nền tường tương phản đơn giản, ánh sáng đủ.',
        'Hai tay thả lỏng tự nhiên bên sườn.'
      ]
    },
    shirt: {
      title: 'Chụp ảnh thân trên',
      tips: [
        'Chụp từ đỉnh đầu xuống quá hông một chút.',
        'Đứng thẳng người, hai vai song song.',
        'Mặc áo ôm vừa để tính toán chính xác.',
        'Tránh mặc áo khoác dày, nhiều nếp gấp.'
      ]
    },
    pants: {
      title: 'Chụp ảnh thân dưới',
      tips: [
        'Chụp từ thắt lưng/hông xuống gót chân.',
        'Hai chân đứng thẳng song song.',
        'Mặc quần ôm hoặc quần short.',
        'Nền tương phản tốt với màu quần.'
      ]
    }
  };

  const currentGuide = guides[garmentType];
  const currentBrand = brands.find((b) => b.name === brand);
  const availableRegions = currentBrand?.available_regions || ['asia'];

  return (
    <SafeAreaView style={styles.container} edges={['top', 'bottom']}>
      {/* Header */}
      <View style={styles.header}>
        <View style={{ flexDirection: 'row', alignItems: 'center' }}>
          <Ionicons name="sparkles" size={22} color="#6366f1" style={{ marginRight: 8 }} />
          <Text style={styles.headerTitle}>Gợi ý Size bằng AI</Text>
        </View>
        <TouchableOpacity onPress={onClose} style={styles.closeButton}>
          <Ionicons name="close" size={24} color="#64748b" />
        </TouchableOpacity>
      </View>

      {/* Steps Progress Indicator (only visible on step 1 and 2) */}
      {(step === 1 || step === 2) && (
        <View style={styles.progressBar}>
          <View style={[styles.progressStep, step >= 1 && styles.progressStepActive]}>
            <Text style={[styles.progressNum, step >= 1 && styles.progressNumActive]}>1</Text>
            <Text style={styles.progressLabel}>Thông số</Text>
          </View>
          <View style={styles.progressLine} />
          <View style={[styles.progressStep, step >= 2 && styles.progressStepActive]}>
            <Text style={[styles.progressNum, step >= 2 && styles.progressNumActive]}>2</Text>
            <Text style={styles.progressLabel}>Chụp ảnh</Text>
          </View>
        </View>
      )}

      {/* STEP 1: Gather Info Form */}
      {step === 1 && (
        <ScrollView style={styles.scrollContent} contentContainerStyle={{ paddingBottom: 30 }}>
          <View style={styles.card}>
            <Text style={styles.cardTitle}>Thông tin cá nhân</Text>
            
            {/* Gender Toggle */}
            <Text style={styles.label}>Giới tính</Text>
            <View style={styles.genderRow}>
              <TouchableOpacity
                style={[styles.genderBtn, gender === 'male' && styles.genderBtnActive]}
                onPress={() => setGender('male')}
              >
                <Text style={[styles.genderText, gender === 'male' && styles.genderTextActive]}>
                  👨 Nam
                </Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.genderBtn, gender === 'female' && styles.genderBtnActive]}
                onPress={() => setGender('female')}
              >
                <Text style={[styles.genderText, gender === 'female' && styles.genderTextActive]}>
                  👩 Nữ
                </Text>
              </TouchableOpacity>
            </View>

            {/* Height & Weight Inputs */}
            <View style={styles.row}>
              <View style={[styles.inputGroup, { marginRight: 12 }]}>
                <Text style={styles.label}>Chiều cao (cm)</Text>
                <TextInput
                  style={styles.textInput}
                  value={height}
                  onChangeText={setHeight}
                  keyboardType="numeric"
                  placeholder="170"
                />
              </View>
              <View style={styles.inputGroup}>
                <Text style={styles.label}>Cân nặng (kg)</Text>
                <TextInput
                  style={styles.textInput}
                  value={weight}
                  onChangeText={setWeight}
                  keyboardType="numeric"
                  placeholder="65"
                />
              </View>
            </View>
          </View>

          <View style={styles.card}>
            <Text style={styles.cardTitle}>Thương hiệu & Dòng đồ</Text>

            {/* Brand Dropdown Sim */}
            <Text style={styles.label}>Thương hiệu quần áo</Text>
            <View style={styles.dropdownSimContainer}>
              {brands.map((b) => (
                <TouchableOpacity
                  key={b.name}
                  style={[styles.chip, brand === b.name && styles.chipActive]}
                  onPress={() => setBrand(b.name)}
                >
                  <Text style={[styles.chipText, brand === b.name && styles.chipTextActive]}>
                    {b.name.toUpperCase()}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>

            {/* Region Dropdown Sim */}
            <Text style={styles.label}>Form size / Khu vực</Text>
            <View style={styles.dropdownSimContainer}>
              {availableRegions.map((r: string) => (
                <TouchableOpacity
                  key={r}
                  style={[styles.chip, region === r && styles.chipActive]}
                  onPress={() => setRegion(r)}
                >
                  <Text style={[styles.chipText, region === r && styles.chipTextActive]}>
                    {r === 'asia' ? 'Châu Á (Asia)' : r.toUpperCase()}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>

            {/* Garment Type Dropdown Sim */}
            <Text style={styles.label}>Sản phẩm muốn đo gợi ý</Text>
            <View style={styles.dropdownSimContainer}>
              <TouchableOpacity
                style={[styles.chip, garmentType === 'both' && styles.chipActive]}
                onPress={() => setGarmentType('both')}
              >
                <Text style={[styles.chipText, garmentType === 'both' && styles.chipTextActive]}>
                  👗 Cả bộ
                </Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.chip, garmentType === 'shirt' && styles.chipActive]}
                onPress={() => setGarmentType('shirt')}
              >
                <Text style={[styles.chipText, garmentType === 'shirt' && styles.chipTextActive]}>
                  👕 Chỉ Áo
                </Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.chip, garmentType === 'pants' && styles.chipActive]}
                onPress={() => setGarmentType('pants')}
              >
                <Text style={[styles.chipText, garmentType === 'pants' && styles.chipTextActive]}>
                  👖 Chỉ Quần
                </Text>
              </TouchableOpacity>
            </View>
          </View>

          {/* Guidelines info */}
          <View style={styles.guideAlert}>
            <View style={{ flexDirection: 'row', alignItems: 'center', marginBottom: 6 }}>
              <Ionicons name="bulb" size={18} color="#eab308" style={{ marginRight: 6 }} />
              <Text style={styles.guideAlertTitle}>{currentGuide.title}</Text>
            </View>
            {currentGuide.tips.map((tip, idx) => (
              <Text key={idx} style={styles.guideTipText}>• {tip}</Text>
            ))}
          </View>

          {/* Action buttons */}
          <View style={styles.btnRow}>
            <TouchableOpacity style={styles.pickerBtn} onPress={handlePickImage}>
              <Ionicons name="images" size={20} color="#6366f1" style={{ marginRight: 6 }} />
              <Text style={styles.pickerBtnText}>Chọn từ máy</Text>
            </TouchableOpacity>
            <TouchableOpacity style={[styles.pickerBtn, styles.pickerBtnPrimary]} onPress={handleTakePhoto}>
              <Ionicons name="camera" size={20} color="#fff" style={{ marginRight: 6 }} />
              <Text style={styles.pickerBtnTextPrimary}>Chụp ảnh thật</Text>
            </TouchableOpacity>
          </View>
        </ScrollView>
      )}

      {/* STEP 2: Image Preview & Confirmation */}
      {step === 2 && (
        <ScrollView style={styles.scrollContent} contentContainerStyle={{ paddingBottom: 30 }}>
          {error && (
            <View style={styles.errorAlert}>
              <Ionicons name="warning" size={20} color="#ef4444" style={{ marginRight: 8 }} />
              <Text style={styles.errorAlertText}>{error}</Text>
            </View>
          )}

          <Text style={styles.previewTitle}>Xác nhận hình ảnh của bạn</Text>
          
          <View style={styles.imagePreviewContainer}>
            {imageUri && (
              <Image source={{ uri: imageUri }} style={styles.previewImage} resizeMode="contain" />
            )}
            <View style={styles.imageOverlayBadge}>
              <Text style={styles.imageOverlayBadgeText}>
                {garmentType === 'both' ? 'Toàn thân' : (garmentType === 'shirt' ? 'Thân trên' : 'Thân dưới')}
              </Text>
            </View>
          </View>

          {/* Options to change or submit */}
          <View style={styles.guideBox}>
            <Text style={styles.guideBoxTitle}>🔍 Kiểm tra trước khi gửi:</Text>
            <Text style={styles.guideTipText}>1. Cơ thể của bạn có nằm ở trung tâm bức ảnh không?</Text>
            <Text style={styles.guideTipText}>2. Quần áo đang mặc không quá thụng hoặc xòe rộng?</Text>
            <Text style={styles.guideTipText}>3. Toàn bộ các khớp đo ({garmentType === 'both' ? 'từ đầu tới chân' : (garmentType === 'shirt' ? 'tay & ngực' : 'eo & chân')}) hiển thị đầy đủ?</Text>
          </View>

          <View style={styles.btnRow}>
            <TouchableOpacity style={styles.backBtn} onPress={() => setStep(1)}>
              <Ionicons name="arrow-back" size={20} color="#64748b" style={{ marginRight: 6 }} />
              <Text style={styles.backBtnText}>Chụp lại / Sửa</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.submitBtn} onPress={() => handlePredict(false)}>
              <Text style={styles.submitBtnText}>✨ Đo Size bằng AI</Text>
              <Ionicons name="arrow-forward" size={20} color="#fff" style={{ marginLeft: 6 }} />
            </TouchableOpacity>
          </View>
        </ScrollView>
      )}

      {/* STEP 3: Loading Page */}
      {step === 3 && (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#6366f1" />
          <Text style={styles.loadingMainText}>AI đang phân tích số đo...</Text>
          <Text style={styles.loadingSubText}>{loadingText}</Text>
          <View style={styles.loadingBarOutline}>
            <View style={styles.loadingBarProgress} />
          </View>
        </View>
      )}

      {/* STEP 4: Prediction Results Page */}
      {step === 4 && prediction && (
        <ScrollView style={styles.scrollContent} contentContainerStyle={{ paddingBottom: 30 }}>
          {prediction.baggy_clothes_detected && (
            <View style={[styles.warningAlert, { marginBottom: 16 }]}>
              <Ionicons name="alert-circle" size={20} color="#d97706" style={{ marginRight: 8 }} />
              <View style={{ flex: 1 }}>
                <Text style={styles.warningAlertTitle}>⚠️ Cảnh báo từ AI</Text>
                <Text style={styles.warningAlertText}>{prediction.warning_message || 'Phát hiện trang phục quá rộng, độ chính xác có thể giảm.'}</Text>
              </View>
            </View>
          )}

          {/* Recommended Size Display Card */}
          <View style={styles.resultCard}>
            <Text style={styles.resultCardSubTitle}>SIZE KHUYÊN DÙNG</Text>
            <View style={styles.mainSizeBadge}>
              <Text style={styles.mainSizeText}>{prediction.predicted_size || 'N/A'}</Text>
            </View>
            <Text style={styles.brandTitleText}>Thương hiệu: {brand.toUpperCase()} ({region.toUpperCase()})</Text>

            {/* Sub-sizes for Shirt & Pants */}
            <View style={styles.subSizesRow}>
              {prediction.shirt_size && (
                <View style={styles.subSizeBox}>
                  <Text style={styles.subSizeLabel}>👕 Khuyên dùng Áo</Text>
                  <Text style={styles.subSizeValue}>{prediction.shirt_size.recommended_size || 'N/A'}</Text>
                  <Text style={styles.subSizeReason}>{prediction.shirt_size.reason || ''}</Text>
                </View>
              )}
              {prediction.pants_size && (
                <View style={styles.subSizeBox}>
                  <Text style={styles.subSizeLabel}>👖 Khuyên dùng Quần</Text>
                  <Text style={styles.subSizeValue}>{prediction.pants_size.recommended_size || 'N/A'}</Text>
                  <Text style={styles.subSizeReason}>{prediction.pants_size.reason || ''}</Text>
                </View>
              )}
            </View>
          </View>

          {/* Measurements Cards */}
          {prediction.measurements && (
            <View style={styles.card}>
              <Text style={styles.cardTitle}>📐 Số đo cơ thể ước tính</Text>
              
              {/* Grid of Measurements */}
              <View style={styles.measurementGrid}>
                {Object.entries(prediction.measurements).map(([key, val]: [string, any]) => {
                  let displayName = key;
                  let emoji = '📏';
                  if (key === 'chest') { displayName = 'Vòng ngực'; emoji = 'Chest 👕'; }
                  if (key === 'waist') { displayName = 'Vòng eo'; emoji = 'Waist 👖'; }
                  if (key === 'hips') { displayName = 'Vòng hông'; emoji = 'Hips 🍑'; }
                  if (key === 'inside_leg') { displayName = 'Chiều dài chân (inseam)'; emoji = 'Inseam 🦵'; }
                  if (key === 'height') { displayName = 'Chiều cao'; emoji = 'Chiều cao 🧍'; }
                  if (key === 'weight') { displayName = 'Cân nặng'; emoji = 'Cân nặng ⚖️'; }

                  const numericValue = typeof val === 'number' ? val.toFixed(1) : val;
                  const unit = key === 'weight' ? 'kg' : 'cm';

                  return (
                    <View key={key} style={styles.measureItem}>
                      <Text style={styles.measureLabel}>{emoji} {displayName}</Text>
                      <Text style={styles.measureValue}>{numericValue} <Text style={styles.measureUnit}>{unit}</Text></Text>
                    </View>
                  );
                })}
              </View>
            </View>
          )}

          {/* Match Details vs Standards */}
          {prediction.match_details && Object.keys(prediction.match_details).length > 0 && (
            <View style={styles.card}>
              <Text style={styles.cardTitle}>📊 So khớp biểu đồ kích cỡ</Text>
              {Object.entries(prediction.match_details).map(([key, detail]: [string, any]) => {
                let displayName = key;
                if (key === 'chest') displayName = 'Vòng ngực';
                if (key === 'waist') displayName = 'Vòng eo';
                if (key === 'hips') displayName = 'Vòng hông';
                if (key === 'inside_leg') displayName = 'Inseam';

                const statusColor = detail.status === 'match' ? '#10b981' : (detail.status === 'tight' ? '#ef4444' : '#f59e0b');
                const statusText = detail.status === 'match' ? 'Vừa vặn' : (detail.status === 'tight' ? 'Hơi chật' : 'Hơi rộng');

                return (
                  <View key={key} style={styles.matchDetailItem}>
                    <View style={styles.matchDetailHeader}>
                      <Text style={styles.matchDetailLabel}>{displayName.toUpperCase()}</Text>
                      <View style={[styles.statusBadge, { backgroundColor: statusColor + '15' }]}>
                        <Text style={[styles.statusText, { color: statusColor }]}>{statusText}</Text>
                      </View>
                    </View>
                    <View style={styles.matchDetailBody}>
                      <Text style={styles.matchDetailVal}>Số đo AI: {detail.value?.toFixed(1)} cm</Text>
                      <Text style={styles.matchDetailRange}>Khoảng chuẩn size: {detail.range ? `${detail.range[0]}-${detail.range[1]} cm` : 'N/A'}</Text>
                    </View>
                  </View>
                );
              })}
            </View>
          )}

          {/* Action buttons */}
          <View style={styles.btnRow}>
            <TouchableOpacity style={styles.backBtn} onPress={() => setStep(1)}>
              <Ionicons name="refresh" size={20} color="#64748b" style={{ marginRight: 6 }} />
              <Text style={styles.backBtnText}>Đo lại</Text>
            </TouchableOpacity>
            <TouchableOpacity style={[styles.submitBtn, { backgroundColor: '#10b981' }]} onPress={handleApplySize}>
              <Text style={styles.submitBtnText}>🛒 Áp dụng Size vào Giỏ hàng</Text>
              <Ionicons name="checkmark-circle" size={20} color="#fff" style={{ marginLeft: 6 }} />
            </TouchableOpacity>
          </View>
        </ScrollView>
      )}

      {/* STEP 5: INTERACTIVE BAGGY WARNING PAGE */}
      {step === 5 && prediction && (
        <View style={[styles.scrollContent, { justifyContent: 'center', alignItems: 'center', padding: 24 }]}>
          <View style={styles.warningCenterCard}>
            <Ionicons name="shirt-outline" size={72} color="#d97706" style={{ marginBottom: 16 }} />
            <Text style={styles.warningCenterTitle}>Phát hiện quần áo quá rộng</Text>
            
            <Text style={styles.warningCenterDesc}>
              Hệ thống AI nhận thấy bạn đang mặc trang phục rộng (Baggy) hoặc đứng chưa chuẩn tư thế. 
              Điều này có thể làm kết quả đo lường tăng thêm và không chính xác.
            </Text>

            <View style={styles.warningImageFrame}>
              {imageUri && <Image source={{ uri: imageUri }} style={styles.warningImageSmall} />}
            </View>

            <Text style={styles.warningQuestion}>Bạn muốn xử lý thế nào?</Text>

            <TouchableOpacity 
              style={[styles.warningButtonAction, { backgroundColor: '#6366f1' }]}
              onPress={() => handlePredict(true)}
            >
              <Ionicons name="arrow-forward" size={20} color="#fff" style={{ marginRight: 8 }} />
              <Text style={styles.warningButtonActionText}>Bỏ qua & Tiếp tục phân tích</Text>
            </TouchableOpacity>

            <TouchableOpacity 
              style={[styles.warningButtonAction, { backgroundColor: '#f1f5f9', borderWidth: 1, borderColor: '#cbd5e1' }]}
              onPress={() => setStep(1)}
            >
              <Ionicons name="camera" size={20} color="#475569" style={{ marginRight: 8 }} />
              <Text style={[styles.warningButtonActionText, { color: '#475569' }]}>Chụp lại ảnh ôm sát hơn</Text>
            </TouchableOpacity>
          </View>
        </View>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingTop: 16,
    paddingBottom: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#e2e8f0',
    backgroundColor: '#fff',
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#0f172a',
  },
  closeButton: {
    padding: 4,
  },
  progressBar: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#fff',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f1f5f9',
  },
  progressStep: {
    flexDirection: 'row',
    alignItems: 'center',
    opacity: 0.5,
  },
  progressStepActive: {
    opacity: 1,
  },
  progressNum: {
    width: 20,
    height: 20,
    borderRadius: 10,
    backgroundColor: '#cbd5e1',
    color: '#fff',
    textAlign: 'center',
    lineHeight: 20,
    fontSize: 11,
    fontWeight: 'bold',
    marginRight: 6,
  },
  progressNumActive: {
    backgroundColor: '#6366f1',
  },
  progressLabel: {
    fontSize: 12,
    fontWeight: '600',
    color: '#334155',
  },
  progressLine: {
    width: 40,
    height: 2,
    backgroundColor: '#cbd5e1',
    marginHorizontal: 12,
  },
  scrollContent: {
    flex: 1,
    padding: 16,
  },
  card: {
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    shadowColor: '#0f172a',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 2,
  },
  cardTitle: {
    fontSize: 15,
    fontWeight: '700',
    color: '#1e293b',
    marginBottom: 14,
  },
  label: {
    fontSize: 13,
    fontWeight: '600',
    color: '#475569',
    marginBottom: 8,
  },
  genderRow: {
    flexDirection: 'row',
    marginBottom: 14,
  },
  genderBtn: {
    flex: 1,
    backgroundColor: '#f1f5f9',
    borderRadius: 10,
    paddingVertical: 12,
    alignItems: 'center',
    marginRight: 8,
    borderWidth: 1.5,
    borderColor: 'transparent',
  },
  genderBtnActive: {
    backgroundColor: '#e0e7ff',
    borderColor: '#6366f1',
  },
  genderText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#475569',
  },
  genderTextActive: {
    color: '#4f46e5',
  },
  row: {
    flexDirection: 'row',
  },
  inputGroup: {
    flex: 1,
  },
  textInput: {
    backgroundColor: '#f1f5f9',
    borderRadius: 10,
    paddingHorizontal: 12,
    paddingVertical: 10,
    fontSize: 14,
    color: '#0f172a',
    borderWidth: 1,
    borderColor: '#cbd5e1',
  },
  dropdownSimContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: 14,
    gap: 8,
  },
  chip: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    backgroundColor: '#f1f5f9',
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#cbd5e1',
  },
  chipActive: {
    backgroundColor: '#e0e7ff',
    borderColor: '#6366f1',
  },
  chipText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#64748b',
  },
  chipTextActive: {
    color: '#4f46e5',
  },
  guideAlert: {
    backgroundColor: '#fef9c3',
    borderWidth: 1,
    borderColor: '#fef08a',
    borderRadius: 12,
    padding: 14,
    marginBottom: 20,
  },
  guideAlertTitle: {
    fontSize: 14,
    fontWeight: '700',
    color: '#854d0e',
  },
  guideTipText: {
    fontSize: 12,
    color: '#713f12',
    lineHeight: 18,
    marginBottom: 2,
  },
  btnRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: 12,
    marginTop: 8,
  },
  pickerBtn: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1.5,
    borderColor: '#cbd5e1',
    backgroundColor: '#fff',
    borderRadius: 12,
    paddingVertical: 14,
  },
  pickerBtnPrimary: {
    borderColor: '#6366f1',
    backgroundColor: '#6366f1',
  },
  pickerBtnText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#6366f1',
  },
  pickerBtnTextPrimary: {
    fontSize: 14,
    fontWeight: '600',
    color: '#fff',
  },
  previewTitle: {
    fontSize: 15,
    fontWeight: '700',
    color: '#334155',
    marginBottom: 10,
    textAlign: 'center',
  },
  imagePreviewContainer: {
    height: 350,
    backgroundColor: '#0f172a',
    borderRadius: 16,
    overflow: 'hidden',
    position: 'relative',
    marginBottom: 16,
    justifyContent: 'center',
    alignItems: 'center',
  },
  previewImage: {
    width: '100%',
    height: '100%',
  },
  imageOverlayBadge: {
    position: 'absolute',
    top: 12,
    right: 12,
    backgroundColor: 'rgba(99, 102, 241, 0.9)',
    borderRadius: 20,
    paddingHorizontal: 12,
    paddingVertical: 6,
  },
  imageOverlayBadgeText: {
    color: '#fff',
    fontSize: 11,
    fontWeight: 'bold',
  },
  guideBox: {
    backgroundColor: '#f1f5f9',
    borderRadius: 12,
    padding: 14,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: '#e2e8f0',
  },
  guideBoxTitle: {
    fontSize: 13,
    fontWeight: '700',
    color: '#334155',
    marginBottom: 6,
  },
  backBtn: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#f1f5f9',
    borderRadius: 12,
    paddingVertical: 14,
    borderWidth: 1,
    borderColor: '#cbd5e1',
  },
  backBtnText: {
    color: '#475569',
    fontSize: 14,
    fontWeight: '600',
  },
  submitBtn: {
    flex: 2,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#6366f1',
    borderRadius: 12,
    paddingVertical: 14,
  },
  submitBtnText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '700',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 30,
    backgroundColor: '#fff',
  },
  loadingMainText: {
    fontSize: 18,
    fontWeight: '700',
    color: '#1e293b',
    marginTop: 20,
  },
  loadingSubText: {
    fontSize: 13,
    color: '#64748b',
    textAlign: 'center',
    marginTop: 8,
    lineHeight: 18,
  },
  loadingBarOutline: {
    width: '80%',
    height: 6,
    backgroundColor: '#f1f5f9',
    borderRadius: 3,
    marginTop: 24,
    overflow: 'hidden',
  },
  loadingBarProgress: {
    width: '45%',
    height: '100%',
    backgroundColor: '#6366f1',
    borderRadius: 3,
  },
  errorAlert: {
    flexDirection: 'row',
    backgroundColor: '#fef2f2',
    borderWidth: 1,
    borderColor: '#fca5a5',
    borderRadius: 12,
    padding: 14,
    marginBottom: 16,
    alignItems: 'center',
  },
  errorAlertText: {
    flex: 1,
    color: '#b91c1c',
    fontSize: 13,
    fontWeight: '500',
  },
  warningAlert: {
    flexDirection: 'row',
    backgroundColor: '#fffbeb',
    borderWidth: 1,
    borderColor: '#fde68a',
    borderRadius: 12,
    padding: 14,
    alignItems: 'flex-start',
  },
  warningAlertTitle: {
    color: '#b45309',
    fontSize: 13,
    fontWeight: '700',
    marginBottom: 2,
  },
  warningAlertText: {
    color: '#b45309',
    fontSize: 12,
    lineHeight: 16,
  },
  resultCard: {
    backgroundColor: '#fff',
    borderRadius: 20,
    padding: 24,
    alignItems: 'center',
    marginBottom: 16,
    borderWidth: 2,
    borderColor: '#6366f1',
    shadowColor: '#6366f1',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 10,
    elevation: 5,
  },
  resultCardSubTitle: {
    fontSize: 11,
    fontWeight: 'bold',
    color: '#6366f1',
    letterSpacing: 2,
    marginBottom: 12,
  },
  mainSizeBadge: {
    width: 90,
    height: 90,
    borderRadius: 45,
    backgroundColor: '#6366f1',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#6366f1',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 4,
    marginBottom: 14,
  },
  mainSizeText: {
    fontSize: 38,
    fontWeight: '900',
    color: '#fff',
  },
  brandTitleText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#64748b',
    marginBottom: 18,
  },
  subSizesRow: {
    flexDirection: 'row',
    borderTopWidth: 1,
    borderTopColor: '#f1f5f9',
    paddingTop: 16,
    width: '100%',
    gap: 12,
  },
  subSizeBox: {
    flex: 1,
    backgroundColor: '#f8fafc',
    borderRadius: 12,
    padding: 12,
    alignItems: 'center',
  },
  subSizeLabel: {
    fontSize: 11,
    fontWeight: '700',
    color: '#475569',
    marginBottom: 4,
  },
  subSizeValue: {
    fontSize: 20,
    fontWeight: '800',
    color: '#0f172a',
    marginBottom: 2,
  },
  subSizeReason: {
    fontSize: 10,
    color: '#64748b',
    textAlign: 'center',
  },
  measurementGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
  },
  measureItem: {
    width: (width - 64 - 10) / 2, // 2 items per row
    backgroundColor: '#f8fafc',
    borderRadius: 12,
    padding: 12,
    borderWidth: 1,
    borderColor: '#f1f5f9',
  },
  measureLabel: {
    fontSize: 11,
    fontWeight: '600',
    color: '#64748b',
    marginBottom: 4,
  },
  measureValue: {
    fontSize: 16,
    fontWeight: '700',
    color: '#0f172a',
  },
  measureUnit: {
    fontSize: 11,
    color: '#94a3b8',
    fontWeight: 'normal',
  },
  matchDetailItem: {
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#f1f5f9',
  },
  matchDetailHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4,
  },
  matchDetailLabel: {
    fontSize: 11,
    fontWeight: '700',
    color: '#475569',
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 10,
  },
  statusText: {
    fontSize: 10,
    fontWeight: 'bold',
  },
  matchDetailBody: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  matchDetailVal: {
    fontSize: 12,
    fontWeight: '600',
    color: '#1e293b',
  },
  matchDetailRange: {
    fontSize: 11,
    color: '#64748b',
  },
  warningCenterCard: {
    backgroundColor: '#fff',
    borderRadius: 24,
    padding: 24,
    alignItems: 'center',
    borderWidth: 1.5,
    borderColor: '#fde68a',
    shadowColor: '#d97706',
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.1,
    shadowRadius: 16,
    elevation: 8,
    width: '100%',
  },
  warningCenterTitle: {
    fontSize: 18,
    fontWeight: '800',
    color: '#b45309',
    marginBottom: 10,
  },
  warningCenterDesc: {
    fontSize: 13,
    color: '#78350f',
    textAlign: 'center',
    lineHeight: 18,
    marginBottom: 20,
  },
  warningImageFrame: {
    width: 140,
    height: 180,
    borderRadius: 12,
    overflow: 'hidden',
    backgroundColor: '#f1f5f9',
    marginBottom: 20,
    borderWidth: 1,
    borderColor: '#cbd5e1',
  },
  warningImageSmall: {
    width: '100%',
    height: '100%',
  },
  warningQuestion: {
    fontSize: 14,
    fontWeight: '700',
    color: '#1e293b',
    marginBottom: 14,
  },
  warningButtonAction: {
    width: '100%',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: 12,
    paddingVertical: 14,
    marginBottom: 10,
  },
  warningButtonActionText: {
    fontSize: 14,
    fontWeight: '700',
    color: '#fff',
  },
});
