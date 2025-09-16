import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  RefreshControl,
  Dimensions,
  Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { LineChart } from 'react-native-chart-kit';

interface DashboardData {
  totalUsers: number;
  totalSales: number;
  totalRevenue: number;
  growthRate: number;
}

interface Activity {
  id: string;
  type: 'sale' | 'user' | 'order';
  message: string;
  timestamp: Date;
  amount?: number;
}

interface DashboardScreenProps {
  navigation?: any;
  user?: {
    name: string;
    avatar?: string;
  };
}

const DashboardScreen: React.FC<DashboardScreenProps> = ({ navigation, user }) => {
  const [dashboardData, setDashboardData] = useState<DashboardData>({
    totalUsers: 1250,
    totalSales: 89,
    totalRevenue: 45680,
    growthRate: 12.5,
  });
  
  const [activities, setActivities] = useState<Activity[]>([
    {
      id: '1',
      type: 'sale',
      message: 'Nova venda realizada',
      timestamp: new Date(Date.now() - 1000 * 60 * 30),
      amount: 299.90,
    },
    {
      id: '2',
      type: 'user',
      message: 'Novo usuário cadastrado',
      timestamp: new Date(Date.now() - 1000 * 60 * 60),
    },
    {
      id: '3',
      type: 'order',
      message: 'Pedido #1234 processado',
      timestamp: new Date(Date.now() - 1000 * 60 * 90),
    },
  ]);
  
  const [refreshing, setRefreshing] = useState(false);
  const screenWidth = Dimensions.get('window').width;

  const chartData = {
    labels: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
    datasets: [
      {
        data: [20, 45, 28, 80, 99, 43],
        strokeWidth: 3,
        color: (opacity = 1) => `rgba(0, 123, 255, ${opacity})`,
      },
    ],
  };

  const onRefresh = async () => {
    setRefreshing(true);
    // Simula atualização de dados
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    setDashboardData(prev => ({
      ...prev,
      totalUsers: prev.totalUsers + Math.floor(Math.random() * 10),
      totalSales: prev.totalSales + Math.floor(Math.random() * 5),
      totalRevenue: prev.totalRevenue + Math.floor(Math.random() * 1000),
    }));
    
    setRefreshing(false);
  };

  const formatCurrency = (value: number): string => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(value);
  };

  const formatTimeAgo = (date: Date): string => {
    const now = new Date();
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));
    
    if (diffInMinutes < 60) {
      return `${diffInMinutes}m atrás`;
    } else if (diffInMinutes < 1440) {
      return `${Math.floor(diffInMinutes / 60)}h atrás`;
    } else {
      return `${Math.floor(diffInMinutes / 1440)}d atrás`;
    }
  };

  const getActivityIcon = (type: Activity['type']) => {
    switch (type) {
      case 'sale':
        return 'card-outline';
      case 'user':
        return 'person-add-outline';
      case 'order':
        return 'bag-outline';
      default:
        return 'notifications-outline';
    }
  };

  const StatCard: React.FC<{
    title: string;
    value: string;
    icon: string;
    color: string;
    growth?: number;
  }> = ({ title, value, icon, color, growth }) => (
    <View style={[styles.statCard, { borderLeftColor: color }]}>
      <View style={styles.statHeader}>
        <View style={[styles.statIcon, { backgroundColor: color + '20' }]}>
          <Ionicons name={icon as any} size={24} color={color} />
        </View>
        {growth !== undefined && (
          <View style={styles.growthContainer}>
            <Ionicons 
              name={growth >= 0 ? 'trending-up' : 'trending-down'} 
              size={16} 
              color={growth >= 0 ? '#28a745' : '#dc3545'} 
            />
            <Text style={[styles.growthText, { color: growth >= 0 ? '#28a745' : '#dc3545' }]}>
              {Math.abs(growth)}%
            </Text>
          </View>
        )}
      </View>
      <Text style={styles.statValue}>{value}</Text>
      <Text style={styles.statTitle}>{title}</Text>
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView 
        style={styles.scrollView}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        showsVerticalScrollIndicator={false}
      >
        {/* Header */}
        <View style={styles.header}>
          <View>
            <Text style={styles.greeting}>Olá, {user?.name || 'Usuário'}!</Text>
            <Text style={styles.subGreeting}>Bem-vindo ao seu dashboard</Text>
          </View>
          <TouchableOpacity 
            style={styles.notificationButton}
            onPress={() => Alert.alert('Notificações', 'Você tem 3 novas notificações')}
            accessibilityLabel="Botão de notificações"
          >
            <Ionicons name="notifications-outline" size={24} color="#333" />
            <View style={styles.notificationBadge}>
              <Text style={styles.notificationBadgeText}>3</Text>
            </View>
          </TouchableOpacity>
        </View>

        {/* Stats Cards */}
        <View style={styles.statsContainer}>
          <StatCard
            title="Total de Usuários"
            value={dashboardData.totalUsers.toLocaleString()}
            icon="people-outline"
            color="#007bff"
            growth={dashboardData.growthRate}
          />
          <StatCard
            title="Vendas Hoje"
            value={dashboardData.totalSales.toString()}
            icon="trending-up-outline"
            color="#28a745"
          />
          <StatCard
            title="Receita Total"
            value={formatCurrency(dashboardData.totalRevenue)}
            icon="card-outline"
            color="#ffc107"
          />
          <StatCard
            title="Taxa de Crescimento"
            value={`${dashboardData.growthRate}%`}
            icon="analytics-outline"
            color="#17a2b8"
          />
        </View>

        {/* Chart Section */}
        <View style={styles.chartContainer}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Vendas dos Últimos 6 Meses</Text>
            <TouchableOpacity onPress={() => navigation?.navigate('Analytics')}>
              <Text style={styles.viewAllText}>Ver tudo</Text>
            </TouchableOpacity>
          </View>
          <View style={styles.chartWrapper}>
            <LineChart
              data={chartData}
              width={screenWidth - 48}
              height={200}
              chartConfig={{
                backgroundColor: '#ffffff',
                backgroundGradientFrom: '#ffffff',
                backgroundGradientTo: '#ffffff',
                decimalPlaces: 0,
                color: (opacity = 1) => `rgba(0, 123, 255, ${opacity})`,
                labelColor: (opacity = 1) => `rgba(0, 0, 0, ${opacity})`,
                style: {
                  borderRadius: 16,
                },
                propsForDots: {
                  r: '6',
                  strokeWidth: '2',
                  stroke: '#007bff',
                },
              }}
              bezier
              style={styles.chart}
            />
          </View>
        </View>

        {/* Recent Activities */}
        <View style={styles.activitiesContainer}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Atividades Recentes</Text>
            <TouchableOpacity onPress={() => navigation?.navigate('Activities')}>
              <Text style={styles.viewAllText}>Ver todas</Text>
            </TouchableOpacity>
          </View>
          
          {activities.map((activity) => (
            <View key={activity.id} style={styles.activityItem}>
              <View style={styles.activityIcon}>
                <Ionicons 
                  name={getActivityIcon(activity.type) as any} 
                  size={20} 
                  color="#007bff" 
                />
              </View>
              <View style={styles.activityContent}>
                <Text style={styles.activityMessage}>{activity.message}</Text>
                <Text style={styles.activityTime}>{formatTimeAgo(activity.timestamp)}</Text>
              </View>
              {activity.amount && (
                <Text style={styles.activityAmount}>
                  {formatCurrency(activity.amount)}
                </Text>
              )}
            </View>
          ))}
        </View>

        {/* Quick Actions */}
        <View style={styles.quickActionsContainer}>
          <Text style={styles.sectionTitle}>Ações Rápidas</Text>
          <View style={styles.quickActionsGrid}>
            <TouchableOpacity 
              style={styles.quickActionButton}
              onPress={() => navigation?.navigate('AddSale')}
            >
              <Ionicons name="add-circle-outline" size={32} color="#007bff" />
              <Text style={styles.quickActionText}>Nova Venda</Text>
            </TouchableOpacity>
            
            <TouchableOpacity 
              style={styles.quickActionButton}
              onPress={() => navigation?.navigate('Reports')}
            >
              <Ionicons name="document-text-outline" size={32} color="#28a745" />
              <Text style={styles.quickActionText}>Relatórios</Text>
            </TouchableOpacity>
            
            <TouchableOpacity 
              style={styles.quickActionButton}
              onPress={() => navigation?.navigate('Settings')}
            >
              <Ionicons name="settings-outline" size={32} color="#ffc107" />
              <Text style={styles.quickActionText}>Configurações</Text>
            </TouchableOpacity>
            
            <TouchableOpacity 
              style={styles.quickActionButton}
              onPress={() => navigation?.navigate('Support')}
            >
              <Ionicons name="help-circle-outline" size={32} color="#17a2b8" />
              <Text style={styles.quickActionText}>Suporte</Text>
            </TouchableOpacity>
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  scrollView: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 24,
    paddingVertical: 20,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e1e5e9',
  },
  greeting: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1a1a1a',
  },
  subGreeting: {
    fontSize: 14,
    color: '#666',
    marginTop: 4,
  },
  notificationButton: {
    position: 'relative',
    padding: 8,
  },
  notificationBadge: {
    position: 'absolute',
    top: 4,
    right: 4,
    backgroundColor: '#ff4757',
    borderRadius: 10,
    minWidth: 20,
    height: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  notificationBadgeText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
  },
  statsContainer: {
    padding: 24,
    gap: 16,
  },
  statCard: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    borderLeftWidth: 4,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  statHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  statIcon: {
    width: 48,
    height: 48,
    borderRadius: 24,
    justifyContent: 'center',
    alignItems: 'center',
  },
  growthContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  growthText: {
    fontSize: 12,
    fontWeight: '600',
  },
  statValue: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1a1a1a',
    marginBottom: 4,
  },
  statTitle: {
    fontSize: 14,
    color: '#666',
  },
  chartContainer: {
    backgroundColor: '#fff',
    marginHorizontal: 24,
    marginBottom: 24,
    borderRadius: 12,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1a1a1a',
  },
  viewAllText: {
    fontSize: 14,
    color: '#007bff',
    fontWeight: '500',
  },
  chartWrapper: {
    alignItems: 'center',
  },
  chart: {
    marginVertical: 8,
    borderRadius: 16,
  },
  activitiesContainer: {
    backgroundColor: '#fff',
    marginHorizontal: 24,
    marginBottom: 24,
    borderRadius: 12,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  activityItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f1f3f4',
  },
  activityIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#007bff20',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  activityContent: {
    flex: 1,
  },
  activityMessage: {
    fontSize: 14,
    color: '#333',
    fontWeight: '500',
  },
  activityTime: {
    fontSize: 12,
    color: '#666',
    marginTop: 2,
  },
  activityAmount: {
    fontSize: 14,
    color: '#28a745',
    fontWeight: '600',
  },
  quickActionsContainer: {
    paddingHorizontal: 24,
    paddingBottom: 24,
  },
  quickActionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 16,
    marginTop: 16,
  },
  quickActionButton: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    alignItems: 'center',
    justifyContent: 'center',
    width: '47%',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  quickActionText: {
    fontSize: 12,
    color: '#333',
    fontWeight: '500',
    marginTop: 8,
    textAlign: 'center',
  },
});

export default DashboardScreen;