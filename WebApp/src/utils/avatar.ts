export function getAvatarUrl(name: string, avatar: string | null): string {
  if (avatar) return avatar
  
  // Генерируем URL для дефолтной аватарки, используя имя пользователя
  const encodedName = encodeURIComponent(name)
  return `https://ui-avatars.com/api/?name=${encodedName}&background=random`
} 