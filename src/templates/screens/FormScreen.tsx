import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
  Alert,
  Switch,
  ActivityIndicator,
} from 'react-native';
import { Picker } from '@react-native-picker/picker';
import DateTimePicker from '@react-native-community/datetimepicker';
import { Ionicons } from '@expo/vector-icons';

interface FormData {
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  birthDate: Date;
  gender: string;
  country: string;
  bio: string;
  notifications: boolean;
  newsletter: boolean;
}

interface FormErrors {
  firstName?: string;
  lastName?: string;
  email?: string;
  phone?: string;
  birthDate?: string;
  country?: string;
  bio?: string;
}

interface FormScreenProps {
  navigation?: any;
  onSubmit?: (data: FormData) => void;
  initialData?: Partial<FormData>;
}

const FormScreen: React.FC<FormScreenProps> = ({ navigation, onSubmit, initialData }) => {
  const [formData, setFormData] = useState<FormData>({
    firstName: initialData?.firstName || '',
    lastName: initialData?.lastName || '',
    email: initialData?.email || '',
    phone: initialData?.phone || '',
    birthDate: initialData?.birthDate || new Date(),
    gender: initialData?.gender || '',
    country: initialData?.country || '',
    bio: initialData?.bio || '',
    notifications: initialData?.notifications || false,
    newsletter: initialData?.newsletter || false,
  });

  const [errors, setErrors] = useState<FormErrors>({});
  const [showDatePicker, setShowDatePicker] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const countries = [
    { label: 'Selecione um país', value: '' },
    { label: 'Brasil', value: 'BR' },
    { label: 'Estados Unidos', value: 'US' },
    { label: 'Argentina', value: 'AR' },
    { label: 'Chile', value: 'CL' },
    { label: 'Colômbia', value: 'CO' },
    { label: 'México', value: 'MX' },
    { label: 'Portugal', value: 'PT' },
  ];

  const genders = [
    { label: 'Selecione o gênero', value: '' },
    { label: 'Masculino', value: 'male' },
    { label: 'Feminino', value: 'female' },
    { label: 'Não binário', value: 'non-binary' },
    { label: 'Prefiro não informar', value: 'prefer-not-to-say' },
  ];

  const validateEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  const validatePhone = (phone: string): boolean => {
    const phoneRegex = /^\(?\d{2}\)?[\s-]?\d{4,5}[\s-]?\d{4}$/;
    return phoneRegex.test(phone.replace(/\D/g, ''));
  };

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};
    let isValid = true;

    // Nome
    if (!formData.firstName.trim()) {
      newErrors.firstName = 'Nome é obrigatório';
      isValid = false;
    } else if (formData.firstName.length < 2) {
      newErrors.firstName = 'Nome deve ter pelo menos 2 caracteres';
      isValid = false;
    }

    // Sobrenome
    if (!formData.lastName.trim()) {
      newErrors.lastName = 'Sobrenome é obrigatório';
      isValid = false;
    } else if (formData.lastName.length < 2) {
      newErrors.lastName = 'Sobrenome deve ter pelo menos 2 caracteres';
      isValid = false;
    }

    // Email
    if (!formData.email.trim()) {
      newErrors.email = 'Email é obrigatório';
      isValid = false;
    } else if (!validateEmail(formData.email)) {
      newErrors.email = 'Email inválido';
      isValid = false;
    }

    // Telefone
    if (!formData.phone.trim()) {
      newErrors.phone = 'Telefone é obrigatório';
      isValid = false;
    } else if (!validatePhone(formData.phone)) {
      newErrors.phone = 'Telefone inválido';
      isValid = false;
    }

    // Data de nascimento
    const today = new Date();
    const age = today.getFullYear() - formData.birthDate.getFullYear();
    if (age < 13) {
      newErrors.birthDate = 'Idade mínima é 13 anos';
      isValid = false;
    } else if (age > 120) {
      newErrors.birthDate = 'Data de nascimento inválida';
      isValid = false;
    }

    // País
    if (!formData.country) {
      newErrors.country = 'País é obrigatório';
      isValid = false;
    }

    // Bio
    if (formData.bio.length > 500) {
      newErrors.bio = 'Bio deve ter no máximo 500 caracteres';
      isValid = false;
    }

    setErrors(newErrors);
    return isValid;
  };

  const handleSubmit = async () => {
    if (!validateForm()) {
      Alert.alert('Erro', 'Por favor, corrija os erros no formulário.');
      return;
    }

    setIsLoading(true);
    try {
      // Simula envio de dados
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      if (onSubmit) {
        onSubmit(formData);
      } else {
        Alert.alert('Sucesso', 'Formulário enviado com sucesso!', [
          { text: 'OK', onPress: () => navigation?.goBack() }
        ]);
      }
    } catch (error) {
      Alert.alert('Erro', 'Falha ao enviar formulário. Tente novamente.');
    } finally {
      setIsLoading(false);
    }
  };

  const formatDate = (date: Date): string => {
    return date.toLocaleDateString('pt-BR');
  };

  const formatPhone = (phone: string): string => {
    const cleaned = phone.replace(/\D/g, '');
    const match = cleaned.match(/^(\d{2})(\d{4,5})(\d{4})$/);
    if (match) {
      return `(${match[1]}) ${match[2]}-${match[3]}`;
    }
    return phone;
  };

  const updateFormData = (field: keyof FormData, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Limpa erro do campo quando usuário começa a digitar
    if (errors[field as keyof FormErrors]) {
      setErrors(prev => ({ ...prev, [field]: undefined }));
    }
  };

  const InputField: React.FC<{
    label: string;
    value: string;
    onChangeText: (text: string) => void;
    placeholder: string;
    error?: string;
    keyboardType?: 'default' | 'email-address' | 'phone-pad';
    multiline?: boolean;
    maxLength?: number;
    icon?: string;
  }> = ({ label, value, onChangeText, placeholder, error, keyboardType = 'default', multiline = false, maxLength, icon }) => (
    <View style={styles.inputContainer}>
      <Text style={styles.label}>{label}</Text>
      <View style={[styles.inputWrapper, error && styles.inputError, multiline && styles.textAreaWrapper]}>
        {icon && (
          <Ionicons name={icon as any} size={20} color="#666" style={styles.inputIcon} />
        )}
        <TextInput
          style={[styles.input, multiline && styles.textArea]}
          placeholder={placeholder}
          placeholderTextColor="#999"
          value={value}
          onChangeText={onChangeText}
          keyboardType={keyboardType}
          multiline={multiline}
          maxLength={maxLength}
          accessibilityLabel={label}
          accessibilityHint={`Digite ${label.toLowerCase()}`}
        />
      </View>
      {maxLength && (
        <Text style={styles.characterCount}>{value.length}/{maxLength}</Text>
      )}
      {error && <Text style={styles.errorText}>{error}</Text>}
    </View>
  );

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView 
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.keyboardView}
      >
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity 
            onPress={() => navigation?.goBack()}
            style={styles.backButton}
            accessibilityLabel="Voltar"
          >
            <Ionicons name="arrow-back" size={24} color="#333" />
          </TouchableOpacity>
          <Text style={styles.headerTitle}>Cadastro</Text>
          <View style={styles.headerSpacer} />
        </View>

        <ScrollView 
          style={styles.scrollView}
          showsVerticalScrollIndicator={false}
          keyboardShouldPersistTaps="handled"
        >
          <View style={styles.form}>
            {/* Informações Pessoais */}
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Informações Pessoais</Text>
              
              <InputField
                label="Nome *"
                value={formData.firstName}
                onChangeText={(text) => updateFormData('firstName', text)}
                placeholder="Digite seu nome"
                error={errors.firstName}
                icon="person-outline"
              />

              <InputField
                label="Sobrenome *"
                value={formData.lastName}
                onChangeText={(text) => updateFormData('lastName', text)}
                placeholder="Digite seu sobrenome"
                error={errors.lastName}
                icon="person-outline"
              />

              <InputField
                label="Email *"
                value={formData.email}
                onChangeText={(text) => updateFormData('email', text.toLowerCase())}
                placeholder="Digite seu email"
                error={errors.email}
                keyboardType="email-address"
                icon="mail-outline"
              />

              <InputField
                label="Telefone *"
                value={formData.phone}
                onChangeText={(text) => updateFormData('phone', formatPhone(text))}
                placeholder="(11) 99999-9999"
                error={errors.phone}
                keyboardType="phone-pad"
                icon="call-outline"
              />
            </View>

            {/* Data de Nascimento */}
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Data de Nascimento</Text>
              <View style={styles.inputContainer}>
                <Text style={styles.label}>Data de Nascimento *</Text>
                <TouchableOpacity 
                  style={[styles.inputWrapper, errors.birthDate && styles.inputError]}
                  onPress={() => setShowDatePicker(true)}
                  accessibilityLabel="Selecionar data de nascimento"
                >
                  <Ionicons name="calendar-outline" size={20} color="#666" style={styles.inputIcon} />
                  <Text style={styles.dateText}>{formatDate(formData.birthDate)}</Text>
                  <Ionicons name="chevron-down" size={20} color="#666" />
                </TouchableOpacity>
                {errors.birthDate && <Text style={styles.errorText}>{errors.birthDate}</Text>}
              </View>
            </View>

            {/* Gênero */}
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Gênero</Text>
              <View style={styles.inputContainer}>
                <Text style={styles.label}>Gênero</Text>
                <View style={styles.pickerWrapper}>
                  <Picker
                    selectedValue={formData.gender}
                    onValueChange={(value) => updateFormData('gender', value)}
                    style={styles.picker}
                    accessibilityLabel="Selecionar gênero"
                  >
                    {genders.map((gender) => (
                      <Picker.Item key={gender.value} label={gender.label} value={gender.value} />
                    ))}
                  </Picker>
                </View>
              </View>
            </View>

            {/* País */}
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Localização</Text>
              <View style={styles.inputContainer}>
                <Text style={styles.label}>País *</Text>
                <View style={[styles.pickerWrapper, errors.country && styles.inputError]}>
                  <Picker
                    selectedValue={formData.country}
                    onValueChange={(value) => updateFormData('country', value)}
                    style={styles.picker}
                    accessibilityLabel="Selecionar país"
                  >
                    {countries.map((country) => (
                      <Picker.Item key={country.value} label={country.label} value={country.value} />
                    ))}
                  </Picker>
                </View>
                {errors.country && <Text style={styles.errorText}>{errors.country}</Text>}
              </View>
            </View>

            {/* Bio */}
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Sobre Você</Text>
              <InputField
                label="Bio"
                value={formData.bio}
                onChangeText={(text) => updateFormData('bio', text)}
                placeholder="Conte um pouco sobre você..."
                error={errors.bio}
                multiline
                maxLength={500}
              />
            </View>

            {/* Preferências */}
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Preferências</Text>
              
              <View style={styles.switchContainer}>
                <View style={styles.switchContent}>
                  <Ionicons name="notifications-outline" size={24} color="#666" />
                  <View style={styles.switchTextContainer}>
                    <Text style={styles.switchLabel}>Notificações Push</Text>
                    <Text style={styles.switchDescription}>Receber notificações no dispositivo</Text>
                  </View>
                </View>
                <Switch
                  value={formData.notifications}
                  onValueChange={(value) => updateFormData('notifications', value)}
                  trackColor={{ false: '#e1e5e9', true: '#007bff' }}
                  thumbColor={formData.notifications ? '#fff' : '#f4f3f4'}
                  accessibilityLabel="Ativar notificações"
                />
              </View>

              <View style={styles.switchContainer}>
                <View style={styles.switchContent}>
                  <Ionicons name="mail-outline" size={24} color="#666" />
                  <View style={styles.switchTextContainer}>
                    <Text style={styles.switchLabel}>Newsletter</Text>
                    <Text style={styles.switchDescription}>Receber emails com novidades</Text>
                  </View>
                </View>
                <Switch
                  value={formData.newsletter}
                  onValueChange={(value) => updateFormData('newsletter', value)}
                  trackColor={{ false: '#e1e5e9', true: '#007bff' }}
                  thumbColor={formData.newsletter ? '#fff' : '#f4f3f4'}
                  accessibilityLabel="Ativar newsletter"
                />
              </View>
            </View>

            {/* Submit Button */}
            <TouchableOpacity 
              style={[styles.submitButton, isLoading && styles.submitButtonDisabled]}
              onPress={handleSubmit}
              disabled={isLoading}
              accessibilityLabel="Enviar formulário"
            >
              {isLoading ? (
                <ActivityIndicator color="#fff" size="small" />
              ) : (
                <Text style={styles.submitButtonText}>Cadastrar</Text>
              )}
            </TouchableOpacity>
          </View>
        </ScrollView>

        {/* Date Picker Modal */}
        {showDatePicker && (
          <DateTimePicker
            value={formData.birthDate}
            mode="date"
            display={Platform.OS === 'ios' ? 'spinner' : 'default'}
            onChange={(event, selectedDate) => {
              setShowDatePicker(false);
              if (selectedDate) {
                updateFormData('birthDate', selectedDate);
              }
            }}
            maximumDate={new Date()}
            minimumDate={new Date(1900, 0, 1)}
          />
        )}
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  keyboardView: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e1e5e9',
  },
  backButton: {
    padding: 8,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1a1a1a',
  },
  headerSpacer: {
    width: 40,
  },
  scrollView: {
    flex: 1,
  },
  form: {
    padding: 24,
  },
  section: {
    marginBottom: 32,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1a1a1a',
    marginBottom: 16,
  },
  inputContainer: {
    marginBottom: 20,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  inputWrapper: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#e1e5e9',
    paddingHorizontal: 16,
    minHeight: 52,
  },
  textAreaWrapper: {
    alignItems: 'flex-start',
    paddingVertical: 16,
  },
  inputError: {
    borderColor: '#ff4757',
  },
  inputIcon: {
    marginRight: 12,
  },
  input: {
    flex: 1,
    fontSize: 16,
    color: '#333',
  },
  textArea: {
    minHeight: 100,
    textAlignVertical: 'top',
  },
  characterCount: {
    fontSize: 12,
    color: '#666',
    textAlign: 'right',
    marginTop: 4,
  },
  errorText: {
    fontSize: 12,
    color: '#ff4757',
    marginTop: 4,
    marginLeft: 4,
  },
  dateText: {
    flex: 1,
    fontSize: 16,
    color: '#333',
  },
  pickerWrapper: {
    backgroundColor: '#fff',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#e1e5e9',
    overflow: 'hidden',
  },
  picker: {
    height: 52,
  },
  switchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#e1e5e9',
  },
  switchContent: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  switchTextContainer: {
    marginLeft: 12,
    flex: 1,
  },
  switchLabel: {
    fontSize: 16,
    fontWeight: '500',
    color: '#333',
  },
  switchDescription: {
    fontSize: 12,
    color: '#666',
    marginTop: 2,
  },
  submitButton: {
    backgroundColor: '#007bff',
    borderRadius: 12,
    height: 52,
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 24,
    shadowColor: '#007bff',
    shadowOffset: {
      width: 0,
      height: 4,
    },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  submitButtonDisabled: {
    backgroundColor: '#ccc',
    shadowOpacity: 0,
    elevation: 0,
  },
  submitButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#fff',
  },
});

export default FormScreen;