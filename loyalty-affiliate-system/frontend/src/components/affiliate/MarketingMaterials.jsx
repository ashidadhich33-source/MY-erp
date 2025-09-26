import { useState } from 'react'
import { useSelector } from 'react-redux'
import {
  Download,
  Image,
  FileText,
  Video,
  Link as LinkIcon,
  Mail,
  MessageSquare,
  Facebook,
  Twitter,
  Instagram,
  Copy,
  ExternalLink
} from 'lucide-react'
import Card from '../ui/Card'
import Button from '../ui/Button'

const MarketingMaterials = () => {
  const [copiedLink, setCopiedLink] = useState(null)
  const { user } = useSelector((state) => state.auth)

  // Mock data - in real app, this would come from API
  const marketingMaterials = [
    {
      id: 1,
      type: 'banner',
      name: 'Affiliate Program Banner (728x90)',
      description: 'Leaderboard banner for websites and blogs',
      format: 'PNG',
      size: '728x90px',
      downloadUrl: '/api/marketing/banner-728x90.png'
    },
    {
      id: 2,
      type: 'banner',
      name: 'Square Banner (300x300)',
      description: 'Perfect for social media posts',
      format: 'PNG',
      size: '300x300px',
      downloadUrl: '/api/marketing/banner-300x300.png'
    },
    {
      id: 3,
      type: 'banner',
      name: 'Vertical Banner (160x600)',
      description: 'Skyscraper banner for sidebars',
      format: 'PNG',
      size: '160x600px',
      downloadUrl: '/api/marketing/banner-160x600.png'
    },
    {
      id: 4,
      type: 'email',
      name: 'Email Template',
      description: 'HTML email template for newsletters',
      format: 'HTML',
      size: 'Responsive',
      downloadUrl: '/api/marketing/email-template.html'
    },
    {
      id: 5,
      type: 'text',
      name: 'Sample Tweets',
      description: 'Ready-to-use tweets and social posts',
      format: 'TXT',
      size: 'Multiple',
      downloadUrl: '/api/marketing/sample-tweets.txt'
    },
    {
      id: 6,
      type: 'video',
      name: 'Product Demo Video',
      description: 'Short promotional video (30 seconds)',
      format: 'MP4',
      size: '1920x1080px',
      downloadUrl: '/api/marketing/demo-video.mp4'
    }
  ]

  const socialMediaTemplates = [
    {
      platform: 'Twitter',
      icon: Twitter,
      color: 'bg-blue-500',
      templates: [
        "🚀 Just joined an amazing affiliate program! Start earning commissions today! #AffiliateMarketing [YOUR_LINK]",
        "💰 Love our loyalty program? Join as an affiliate and earn money for referrals! [YOUR_LINK] #PassiveIncome",
        "🎯 Looking for a side hustle? Our affiliate program offers competitive commissions! [YOUR_LINK] #Affiliate"
      ]
    },
    {
      platform: 'Facebook',
      icon: Facebook,
      color: 'bg-blue-600',
      templates: [
        "Excited to announce I'm now an affiliate partner! If you love our loyalty program as much as I do, join through my link and I'll earn a commission. Win-win! [YOUR_LINK]",
        "💼 Side hustle alert! Our affiliate program lets you earn money by sharing something you already love. Check it out! [YOUR_LINK]",
        "👥 Friends and family: If you're interested in our loyalty program, I'd love to be your affiliate sponsor! [YOUR_LINK]"
      ]
    },
    {
      platform: 'Instagram',
      icon: Instagram,
      color: 'bg-pink-500',
      templates: [
        "Just became an affiliate! 🎉 If you're looking for a great loyalty program, check out my link in bio! 💰",
        "New side hustle unlocked! 🔓 Our affiliate program is amazing. Link in bio! 💼",
        "Love our loyalty program? So do I! Join through my affiliate link and help me earn commissions! ❤️ [LINK]"
      ]
    }
  ]

  const emailTemplates = [
    {
      subject: "You Won't Believe This Amazing Loyalty Program!",
      content: `Hi [Friend's Name],

I just discovered this incredible loyalty program and had to share it with you!

They offer:
• Points on every purchase
• Multiple reward tiers (Bronze, Silver, Gold, Platinum)
• Exclusive member benefits
• Birthday rewards and special promotions

The best part? If you join through my affiliate link, I earn a commission and you get all the benefits!

Check it out here: [YOUR_AFFILIATE_LINK]

Let me know if you have any questions!

Best,
[Your Name]`
    },
    {
      subject: "Earn Rewards While Shopping - Join Today!",
      content: `Hey [Friend's Name],

I wanted to let you know about this fantastic loyalty program I've been using:

✅ Earn points on every purchase
✅ Redeem for free items and discounts
✅ Multiple membership tiers with increasing benefits
✅ Mobile app for easy tracking

It's completely free to join and the rewards add up quickly!

Use my affiliate link to sign up: [YOUR_AFFILIATE_LINK]

Happy shopping!
[Your Name]`
    }
  ]

  const copyToClipboard = (text, type) => {
    navigator.clipboard.writeText(text)
    setCopiedLink(type)
    setTimeout(() => setCopiedLink(null), 2000)
  }

  const downloadMaterial = (material) => {
    // In a real app, this would trigger a download
    console.log(`Downloading ${material.name}`)
    alert(`Download started for ${material.name}`)
  }

  const getTypeIcon = (type) => {
    switch (type) {
      case 'banner':
        return <Image className="h-5 w-5" />
      case 'email':
        return <Mail className="h-5 w-5" />
      case 'text':
        return <FileText className="h-5 w-5" />
      case 'video':
        return <Video className="h-5 w-5" />
      default:
        return <FileText className="h-5 w-5" />
    }
  }

  const getTypeColor = (type) => {
    switch (type) {
      case 'banner':
        return 'bg-blue-100 text-blue-800'
      case 'email':
        return 'bg-green-100 text-green-800'
      case 'text':
        return 'bg-purple-100 text-purple-800'
      case 'video':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Marketing Materials</h2>
        <p className="text-gray-600">
          Download promotional materials and templates to help you promote our affiliate program.
        </p>
      </div>

      {/* Downloadable Materials */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Download Materials</h3>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {marketingMaterials.map(material => (
            <div key={material.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-3">
                <div className={`p-2 rounded-lg ${getTypeColor(material.type)}`}>
                  {getTypeIcon(material.type)}
                </div>
                <span className={`px-2 py-1 text-xs font-medium rounded-full ${getTypeColor(material.type)}`}>
                  {material.format}
                </span>
              </div>

              <h4 className="font-medium text-gray-900 mb-2">{material.name}</h4>
              <p className="text-sm text-gray-600 mb-3">{material.description}</p>

              <div className="text-xs text-gray-500 mb-4">
                Size: {material.size}
              </div>

              <Button
                onClick={() => downloadMaterial(material)}
                className="w-full"
                size="sm"
              >
                <Download className="h-4 w-4 mr-2" />
                Download
              </Button>
            </div>
          ))}
        </div>
      </Card>

      {/* Social Media Templates */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Social Media Templates</h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {socialMediaTemplates.map(platform => {
            const Icon = platform.icon
            return (
              <div key={platform.platform} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center mb-4">
                  <div className={`p-2 rounded-lg ${platform.color} text-white mr-3`}>
                    <Icon className="h-5 w-5" />
                  </div>
                  <h4 className="font-medium text-gray-900">{platform.platform}</h4>
                </div>

                <div className="space-y-3">
                  {platform.templates.map((template, index) => (
                    <div key={index} className="bg-gray-50 p-3 rounded text-sm">
                      <p className="text-gray-700 mb-2">{template.replace('[YOUR_LINK]', 'https://loyaltyapp.com/ref/AFF123')}</p>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => copyToClipboard(
                          template.replace('[YOUR_LINK]', 'https://loyaltyapp.com/ref/AFF123'),
                          `${platform.platform}-${index}`
                        )}
                        className="w-full"
                      >
                        {copiedLink === `${platform.platform}-${index}` ? (
                          <>
                            <span className="text-green-600 mr-2">✓</span>
                            Copied!
                          </>
                        ) : (
                          <>
                            <Copy className="h-3 w-3 mr-2" />
                            Copy
                          </>
                        )}
                      </Button>
                    </div>
                  ))}
                </div>
              </div>
            )
          })}
        </div>
      </Card>

      {/* Email Templates */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Email Templates</h3>

        <div className="space-y-6">
          {emailTemplates.map((template, index) => (
            <div key={index} className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h4 className="font-medium text-gray-900">{template.subject}</h4>
                  <p className="text-sm text-gray-600 mt-1">
                    Perfect for sending to friends and family
                  </p>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => copyToClipboard(template.content, `email-${index}`)}
                >
                  {copiedLink === `email-${index}` ? (
                    <>
                      <span className="text-green-600 mr-2">✓</span>
                      Copied!
                    </>
                  ) : (
                    <>
                      <Copy className="h-4 w-4 mr-2" />
                      Copy
                    </>
                  )}
                </Button>
              </div>

              <div className="bg-gray-50 p-4 rounded text-sm">
                <pre className="whitespace-pre-wrap text-gray-700 font-mono text-xs">
                  {template.content.replace('[YOUR_AFFILIATE_LINK]', 'https://loyaltyapp.com/ref/AFF123')}
                </pre>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Best Practices */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Best Practices</h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium text-gray-900 mb-3">Do's ✅</h4>
            <ul className="space-y-2 text-sm text-gray-600">
              <li>• Share your genuine experience with the program</li>
              <li>• Use the materials we've provided</li>
              <li>• Be transparent about being an affiliate</li>
              <li>• Target audiences who would genuinely benefit</li>
              <li>• Track your results and optimize</li>
            </ul>
          </div>

          <div>
            <h4 className="font-medium text-gray-900 mb-3">Don'ts ❌</h4>
            <ul className="space-y-2 text-sm text-gray-600">
              <li>• Don't spam your audience</li>
              <li>• Don't make false claims about the program</li>
              <li>• Don't use deceptive marketing tactics</li>
              <li>• Don't share your affiliate link inappropriately</li>
              <li>• Don't violate platform terms of service</li>
            </ul>
          </div>
        </div>

        <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <h4 className="font-medium text-blue-900 mb-2">Need Help?</h4>
          <p className="text-sm text-blue-800">
            If you need custom marketing materials, have questions about compliance,
            or want to discuss marketing strategies, contact our affiliate support team.
          </p>
        </div>
      </Card>
    </div>
  )
}

export default MarketingMaterials