/**
 * ########################
 * #  App data contracts  #
 * ########################
 * Pure JSDoc typedefs for IntelliSense in JS projects.
 */

/** @typedef {'manager'|'salesman'} UserRole */

/**
 * @typedef {Object} User
 * @property {string} id
 * @property {string} name
 * @property {string} email
 * @property {UserRole} role
 */

/**
 * @typedef {Object} AuthResponse
 * @property {string} token
 * @property {User} user
 */

/**
 * @typedef {Object} KPI
 * @property {number} total
 * @property {number} target
 * @property {number[]} trend
 */

/**
 * @typedef {Object} Sale
 * @property {string} id
 * @property {string} agentId
 * @property {string} [agentName]
 * @property {number} amount
 * @property {string} date           ISO date
 * @property {string} [region]
 */

/**
 * @typedef {Object} SalesSummary
 * @property {number} revenue
 * @property {number} target
 * @property {number} deals
 * @property {number} winRatePct
 * @property {number} [deltaRevenuePct]
 * @property {number[]} trend
 */

/**
 * @typedef {Object} Agent
 * @property {string} id
 * @property {string} name
 * @property {string} [region]
 * @property {number} [revenue]
 * @property {number} [achievementsCount]
 */

/**
 * @typedef {'bronze'|'silver'|'gold'} AchievementTier
 */

/**
 * @typedef {Object} Achievement
 * @property {string} id
 * @property {AchievementTier} tier
 * @property {string} [label]
 * @property {string} [earnedAt]  ISO date
 * @property {number} [points]
 */

/**
 * @typedef {Object} Feedback
 * @property {string} id
 * @property {string} title
 * @property {string} body
 * @property {string} createdAt   ISO datetime
 * @property {boolean} read
 * @property {string} [agentId]
 */

/** @typedef {'user'|'ai'} ChatAuthor */

/**
 * @typedef {Object} ChatMessage
 * @property {string} id
 * @property {ChatAuthor} author
 * @property {string} content
 * @property {string} createdAt    ISO datetime
 */

/**
 * @typedef {Object} ChatSession
 * @property {string} id
 * @property {ChatMessage[]} messages
 * @property {string} createdAt
 */

/**
 * @template T
 * @typedef {Object} Paged
 * @property {T[]} items
 * @property {number} total
 * @property {number} page
 * @property {number} pageSize
 */
