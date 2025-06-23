import navigationAttributes from '../navigation_attributes.json'

// Create category mapping from the actual database
export class CategoryMapper {
  private static instance: CategoryMapper
  private categoryMap: Map<string, string[]>
  private brandMap: Map<string, string[]>
  private usageMap: Map<string, string[]>

  private constructor() {
    this.categoryMap = new Map()
    this.brandMap = new Map()
    this.usageMap = new Map()
    this.initializeMaps()
  }

  static getInstance(): CategoryMapper {
    if (!CategoryMapper.instance) {
      CategoryMapper.instance = new CategoryMapper()
    }
    return CategoryMapper.instance
  }

  private initializeMaps() {
    // Initialize category mappings from actual database
    this.setupCategoryMap()
    this.setupBrandMap()
    this.setupUsageMap()
  }

  private setupCategoryMap() {
    // Map Thai user terms to actual database categories
    this.categoryMap.set('โน้ตบุ๊ก', ['NOTEBOOKS', 'Notebooks', 'Gaming Notebooks', 'Ultrathin Notebooks', '2 in 1 Notebooks'])
    this.categoryMap.set('laptop', ['NOTEBOOKS', 'Notebooks', 'Gaming Notebooks', 'Ultrathin Notebooks', '2 in 1 Notebooks'])
    this.categoryMap.set('notebook', ['NOTEBOOKS', 'Notebooks', 'Gaming Notebooks', 'Ultrathin Notebooks', '2 in 1 Notebooks'])
    
    this.categoryMap.set('คีย์บอร์ด', ['KEYBOARD / MOUSE / PEN TABLET', 'Keyboard', 'Mechanical & Gaming Keyboard', 'Wireless Keyboard', 'Keyboard & Mouse Combo'])
    this.categoryMap.set('keyboard', ['KEYBOARD / MOUSE / PEN TABLET', 'Keyboard', 'Mechanical & Gaming Keyboard', 'Wireless Keyboard', 'Keyboard & Mouse Combo'])
    
    this.categoryMap.set('เมาส์', ['KEYBOARD / MOUSE / PEN TABLET', 'Mouse', 'Gaming Mouse', 'Wireless Mouse'])
    this.categoryMap.set('mouse', ['KEYBOARD / MOUSE / PEN TABLET', 'Mouse', 'Gaming Mouse', 'Wireless Mouse'])
    
    this.categoryMap.set('จอมอนิเตอร์', ['MONITOR ', 'Monitor'])
    this.categoryMap.set('จอ', ['MONITOR ', 'Monitor'])
    this.categoryMap.set('monitor', ['MONITOR ', 'Monitor'])
    
    this.categoryMap.set('การ์ดจอ', ['COMPUTER HARDWARE (DIY)', 'Graphics Cards'])
    this.categoryMap.set('vga', ['COMPUTER HARDWARE (DIY)', 'Graphics Cards'])
    this.categoryMap.set('graphics', ['COMPUTER HARDWARE (DIY)', 'Graphics Cards'])
    
    this.categoryMap.set('ซีพียู', ['COMPUTER HARDWARE (DIY)', 'CPU'])
    this.categoryMap.set('cpu', ['COMPUTER HARDWARE (DIY)', 'CPU'])
    this.categoryMap.set('processor', ['COMPUTER HARDWARE (DIY)', 'CPU'])
    
    this.categoryMap.set('หูฟัง', ['SPEAKER / HEADSET', 'Headphone', 'Headset', 'In Ear Headphone', 'True Wireless Headphone'])
    this.categoryMap.set('headphone', ['SPEAKER / HEADSET', 'Headphone', 'Headset', 'In Ear Headphone', 'True Wireless Headphone'])
    this.categoryMap.set('headset', ['SPEAKER / HEADSET', 'Headphone', 'Headset', 'In Ear Headphone', 'True Wireless Headphone'])
    
    this.categoryMap.set('เมนบอร์ด', ['COMPUTER HARDWARE (DIY)', 'Mainboards'])
    this.categoryMap.set('mainboard', ['COMPUTER HARDWARE (DIY)', 'Mainboards'])
    this.categoryMap.set('motherboard', ['COMPUTER HARDWARE (DIY)', 'Mainboards'])
    
    this.categoryMap.set('แรม', ['COMPUTER HARDWARE (DIY)', 'RAM', 'Notebook RAM (SO-DIMM)'])
    this.categoryMap.set('ram', ['COMPUTER HARDWARE (DIY)', 'RAM', 'Notebook RAM (SO-DIMM)'])
    this.categoryMap.set('memory', ['COMPUTER HARDWARE (DIY)', 'RAM', 'Notebook RAM (SO-DIMM)'])
    
    this.categoryMap.set('เคส', ['COMPUTER HARDWARE (DIY)', 'Case & Power Supply', 'Computer Case'])
    this.categoryMap.set('case', ['COMPUTER HARDWARE (DIY)', 'Case & Power Supply', 'Computer Case'])
    
    this.categoryMap.set('พาวเวอร์', ['COMPUTER HARDWARE (DIY)', 'Case & Power Supply', 'Power Supply'])
    this.categoryMap.set('power', ['COMPUTER HARDWARE (DIY)', 'Case & Power Supply', 'Power Supply'])
    this.categoryMap.set('psu', ['COMPUTER HARDWARE (DIY)', 'Case & Power Supply', 'Power Supply'])
    
    this.categoryMap.set('ฮาร์ดดิสก์', ['MEMORY CARD / HARD DRIVE', 'Hard Drive & Solid State Drive', 'Notebook HDD'])
    this.categoryMap.set('hdd', ['MEMORY CARD / HARD DRIVE', 'Hard Drive & Solid State Drive', 'Notebook HDD'])
    this.categoryMap.set('harddisk', ['MEMORY CARD / HARD DRIVE', 'Hard Drive & Solid State Drive', 'Notebook HDD'])
    
    this.categoryMap.set('เอสเอสดี', ['MEMORY CARD / HARD DRIVE', 'Hard Drive & Solid State Drive', 'M.2 SSD'])
    this.categoryMap.set('ssd', ['MEMORY CARD / HARD DRIVE', 'Hard Drive & Solid State Drive', 'M.2 SSD'])
    
    this.categoryMap.set('สปีกเกอร์', ['SPEAKER / HEADSET', 'Speaker', 'Bluetooth Speaker'])
    this.categoryMap.set('speaker', ['SPEAKER / HEADSET', 'Speaker', 'Bluetooth Speaker'])
    
    this.categoryMap.set('เว็บแคม', ['WEBCAM / CONFERENCE', 'Webcam'])
    this.categoryMap.set('webcam', ['WEBCAM / CONFERENCE', 'Webcam'])
    
    this.categoryMap.set('เครื่องพิมพ์', ['PRINTER / INK / TONER / DRUM / SCANNER', 'Printer'])
    this.categoryMap.set('printer', ['PRINTER / INK / TONER / DRUM / SCANNER', 'Printer'])
    
    this.categoryMap.set('เกมมิ่งเกียร์', ['GAMING GEAR ', 'Gaming Accessories', 'Gaming Chair', 'Gaming Desk'])
    this.categoryMap.set('gaming', ['GAMING GEAR ', 'Gaming Accessories', 'Gaming Chair', 'Gaming Desk'])
  }

  private setupBrandMap() {
    // Extract brands from categoryMessage3
    const brands = [
      'ASUS', 'MSI', 'Gigabyte', 'Asrock', 'Intel', 'AMD', 
      'Kingston', 'Corsair', 'Logitech', 'Razer', 'SteelSeries',
      'HyperX', 'Cooler Master', 'NZXT', 'Thermaltake', 'Acer',
      'HP', 'Dell', 'Lenovo', 'Apple', 'Samsung', 'LG', 'AOC',
      'BenQ', 'Asus', 'Creative', 'JBL', 'Sony', 'Philips',
      'Keychron', 'Ducky', 'Glorious', 'Fantech', 'Redragon',
      'HyperX', 'Anker', 'Belkin', 'TP-Link', 'D-Link'
    ]
    
    brands.forEach(brand => {
      this.brandMap.set(brand.toLowerCase(), [brand])
      // Add Thai variants if needed
      if (brand === 'ASUS') this.brandMap.set('เอซุส', [brand])
      if (brand === 'AMD') this.brandMap.set('เอเอ็มดี', [brand])
      if (brand === 'Intel') this.brandMap.set('อินเทล', [brand])
    })
  }

  private setupUsageMap() {
    this.usageMap.set('เล่นเกม', ['Gaming', 'เกมมิ่ง'])
    this.usageMap.set('gaming', ['Gaming', 'เกมมิ่ง'])
    this.usageMap.set('เกมมิ่ง', ['Gaming', 'เกมมิ่ง'])
    
    this.usageMap.set('ทำงาน', ['Office', 'Business', 'Work'])
    this.usageMap.set('work', ['Office', 'Business', 'Work'])
    this.usageMap.set('office', ['Office', 'Business', 'Work'])
    
    this.usageMap.set('เรียน', ['Student', 'Education'])
    this.usageMap.set('student', ['Student', 'Education'])
    this.usageMap.set('education', ['Student', 'Education'])
    
    this.usageMap.set('กราฟิก', ['Graphics', 'Design', 'Creative'])
    this.usageMap.set('design', ['Graphics', 'Design', 'Creative'])
    this.usageMap.set('creative', ['Graphics', 'Design', 'Creative'])
    
    this.usageMap.set('โปรแกรม', ['Programming', 'Developer'])
    this.usageMap.set('programming', ['Programming', 'Developer'])
    this.usageMap.set('coding', ['Programming', 'Developer'])
    
    this.usageMap.set('วิดีโอ', ['Video', 'Streaming', 'Content Creator'])
    this.usageMap.set('video', ['Video', 'Streaming', 'Content Creator'])
    this.usageMap.set('streaming', ['Video', 'Streaming', 'Content Creator'])
  }

  // Get actual database categories for a user input
  getCategoryTerms(userInput: string): string[] {
    const input = userInput.toLowerCase()
    const allTerms: string[] = []
    
    for (const [key, values] of this.categoryMap.entries()) {
      if (input.includes(key.toLowerCase())) {
        allTerms.push(...values)
      }
    }
    
    return [...new Set(allTerms)]
  }

  getBrandTerms(userInput: string): string[] {
    const input = userInput.toLowerCase()
    const allTerms: string[] = []
    
    for (const [key, values] of this.brandMap.entries()) {
      if (input.includes(key.toLowerCase())) {
        allTerms.push(...values)
      }
    }
    
    return [...new Set(allTerms)]
  }

  getUsageTerms(userInput: string): string[] {
    const input = userInput.toLowerCase()
    const allTerms: string[] = []
    
    for (const [key, values] of this.usageMap.entries()) {
      if (input.includes(key.toLowerCase())) {
        allTerms.push(...values)
      }
    }
    
    return [...new Set(allTerms)]
  }

  // Get all available categories for LLM context
  getAllCategories() {
    return {
      categoryMessage1: navigationAttributes.categoryMessage1,
      categoryMessage2: navigationAttributes.categoryMessage2.filter(Boolean),
      categoryMessage3: navigationAttributes.categoryMessage3.filter(Boolean)
    }
  }
}