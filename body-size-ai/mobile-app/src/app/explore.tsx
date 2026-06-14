import React from 'react';
import {
  StyleSheet,
  View,
  Text,
  ScrollView,
  SafeAreaView,
  Dimensions,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';

const { width } = Dimensions.get('window');

export default function SizeGuideScreen() {
  const sizeChart = [
    { size: 'XS', chest: '78-82 cm', waist: '62-66 cm', hips: '86-90 cm', height: '150-160 cm' },
    { size: 'S', chest: '82-86 cm', waist: '66-70 cm', hips: '90-94 cm', height: '155-165 cm' },
    { size: 'M', chest: '86-90 cm', waist: '70-74 cm', hips: '94-98 cm', height: '160-170 cm' },
    { size: 'L', chest: '90-94 cm', waist: '74-78 cm', hips: '98-102 cm', height: '165-175 cm' },
    { size: 'XL', chest: '94-98 cm', waist: '78-82 cm', hips: '102-106 cm', height: '170-180 cm' },
    { size: 'XXL', chest: '98-102 cm', waist: '82-86 cm', hips: '106-110 cm', height: '175-185 cm' },
  ];

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView style={styles.container} contentContainerStyle={{ paddingBottom: 40 }}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.headerTitle}>Trung tâm Hướng dẫn AI</Text>
        </View>

        {/* Hero Section */}
        <View style={styles.heroBox}>
          <Ionicons name="shield-checkmark" size={48} color="#6366f1" style={{ marginBottom: 12 }} />
          <Text style={styles.heroTitle}>Bí quyết đo chính xác 98%</Text>
          <Text style={styles.heroDesc}>
            Công nghệ đo lường nhân trắc học qua hình ảnh của chúng tôi được phát triển dựa trên hàng ngàn điểm dữ liệu cơ thể thực tế. Hãy theo dõi các hướng dẫn dưới đây để có kết quả chính xác nhất.
          </Text>
        </View>

        {/* Photo Guidelines Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>📸 3 Bước Chuẩn Bị Chụp Ảnh</Text>
          
          {/* Card 1 */}
          <View style={styles.guideCard}>
            <View style={styles.guideCardHeader}>
              <View style={styles.stepBadge}>
                <Text style={styles.stepBadgeText}>1</Text>
              </View>
              <Text style={styles.guideCardTitle}>Tư thế đứng thẳng (Pose)</Text>
            </View>
            <Text style={styles.guideCardBody}>
              Đứng thẳng người tự nhiên, hai vai cân bằng song song, chân hơi khép hờ. Hai tay buông dọc sát sườn, lòng bàn tay hướng nhẹ vào trong cơ thể. Không khoanh tay hay tạo dáng nghiêng người.
            </Text>
          </View>

          {/* Card 2 */}
          <View style={styles.guideCard}>
            <View style={styles.guideCardHeader}>
              <View style={styles.stepBadge}>
                <Text style={styles.stepBadgeText}>2</Text>
              </View>
              <Text style={styles.guideCardTitle}>Trang phục ôm vừa vặn</Text>
            </View>
            <Text style={styles.guideCardBody}>
              Đây là yếu tố quan trọng nhất. Hãy mặc các loại áo phông thun, quần đùi thun, legging hoặc trang phục thể thao ôm vừa sát cơ thể. Tránh xa áo khoác phao, quần ống rộng, váy xoè vì AI sẽ bị đo nhầm biên đồ rộng thành kích cỡ cơ thể.
            </Text>
          </View>

          {/* Card 3 */}
          <View style={styles.guideCard}>
            <View style={styles.guideCardHeader}>
              <View style={styles.stepBadge}>
                <Text style={styles.stepBadgeText}>3</Text>
              </View>
              <Text style={styles.guideCardTitle}>Nền tương phản tốt</Text>
            </View>
            <Text style={styles.guideCardBody}>
              Nên chụp đứng trước một bức tường phẳng đơn sắc (như tường trắng, xám, kem) có ánh sáng chiếu sáng đều từ phía trước. Tránh đứng ngược sáng (đứng trước cửa sổ mở rộng) làm cơ thể bị tối đen.
            </Text>
          </View>
        </View>

        {/* Sizing Chart Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>📊 Bảng Size Tiêu Chuẩn</Text>
          <Text style={styles.tableSubtitle}>Tham khảo kích thước tương ứng cho dòng Generic (Châu Á):</Text>
          
          <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.tableScroll}>
            <View style={styles.tableContainer}>
              {/* Table Header */}
              <View style={styles.tableHeaderRow}>
                <Text style={[styles.cellHeader, { width: 50 }]}>Size</Text>
                <Text style={[styles.cellHeader, { width: 90 }]}>Vòng ngực</Text>
                <Text style={[styles.cellHeader, { width: 90 }]}>Vòng eo</Text>
                <Text style={[styles.cellHeader, { width: 90 }]}>Vòng hông</Text>
                <Text style={[styles.cellHeader, { width: 100 }]}>Chiều cao phù hợp</Text>
              </View>

              {/* Table Body */}
              {sizeChart.map((row, idx) => (
                <View key={idx} style={[styles.tableRow, idx % 2 === 1 && styles.tableRowAlt]}>
                  <Text style={[styles.cell, { width: 50, fontWeight: 'bold', color: '#6366f1' }]}>{row.size}</Text>
                  <Text style={[styles.cell, { width: 90 }]}>{row.chest}</Text>
                  <Text style={[styles.cell, { width: 90 }]}>{row.waist}</Text>
                  <Text style={[styles.cell, { width: 90 }]}>{row.hips}</Text>
                  <Text style={[styles.cell, { width: 100 }]}>{row.height}</Text>
                </View>
              ))}
            </View>
          </ScrollView>
        </View>

        {/* Privacy Note */}
        <View style={styles.privacyBox}>
          <Ionicons name="lock-closed" size={20} color="#10b981" style={{ marginRight: 8 }} />
          <Text style={styles.privacyText}>
            Hình ảnh của bạn được xử lý an toàn, tuân thủ chính sách bảo mật và sẽ bị xóa ngay khỏi bộ nhớ đệm máy chủ sau khi tính toán xong số đo cơ thể.
          </Text>
        </View>
      </ScrollView>
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
  header: {
    paddingHorizontal: 20,
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#f1f5f9',
    backgroundColor: '#fff',
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#0f172a',
  },
  heroBox: {
    margin: 16,
    backgroundColor: '#fff',
    borderRadius: 16,
    padding: 20,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#e2e8f0',
  },
  heroTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1e293b',
    marginBottom: 6,
  },
  heroDesc: {
    fontSize: 12,
    color: '#64748b',
    textAlign: 'center',
    lineHeight: 18,
  },
  section: {
    marginHorizontal: 16,
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 15,
    fontWeight: 'bold',
    color: '#0f172a',
    marginBottom: 12,
  },
  guideCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#e2e8f0',
  },
  guideCardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  stepBadge: {
    width: 22,
    height: 22,
    borderRadius: 11,
    backgroundColor: '#e0e7ff',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 8,
  },
  stepBadgeText: {
    fontSize: 11,
    fontWeight: 'bold',
    color: '#6366f1',
  },
  guideCardTitle: {
    fontSize: 14,
    fontWeight: '700',
    color: '#334155',
  },
  guideCardBody: {
    fontSize: 12,
    color: '#64748b',
    lineHeight: 18,
  },
  tableSubtitle: {
    fontSize: 12,
    color: '#64748b',
    marginBottom: 8,
  },
  tableScroll: {
    backgroundColor: '#fff',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#e2e8f0',
    overflow: 'hidden',
  },
  tableContainer: {
    padding: 8,
  },
  tableHeaderRow: {
    flexDirection: 'row',
    borderBottomWidth: 1.5,
    borderBottomColor: '#e2e8f0',
    paddingVertical: 8,
  },
  cellHeader: {
    fontSize: 11,
    fontWeight: 'bold',
    color: '#475569',
    textAlign: 'center',
  },
  tableRow: {
    flexDirection: 'row',
    borderBottomWidth: 1,
    borderBottomColor: '#f1f5f9',
    paddingVertical: 10,
    alignItems: 'center',
  },
  tableRowAlt: {
    backgroundColor: '#f8fafc',
  },
  cell: {
    fontSize: 11,
    color: '#475569',
    textAlign: 'center',
  },
  privacyBox: {
    flexDirection: 'row',
    margin: 16,
    backgroundColor: '#ecfdf5',
    borderWidth: 1,
    borderColor: '#a7f3d0',
    borderRadius: 12,
    padding: 14,
    alignItems: 'center',
  },
  privacyText: {
    flex: 1,
    fontSize: 11,
    color: '#065f46',
    lineHeight: 16,
  },
});
